"""Lemon Squeezy billing adapter.

Implements hosted checkout creation and webhook verification/parsing against
the Lemon Squeezy API. Reads configuration from ``current_app.config`` at call
time, so it operates within a Flask request context.
"""
import hashlib
import hmac
import json
from datetime import datetime
from typing import Dict, Optional

import requests
from flask import current_app

from ..plans import PLANS
from .base import (
    BillingWebhookResult,
    ProviderNotConfiguredError,
    WebhookVerificationError,
)

_API_BASE = 'https://api.lemonsqueezy.com/v1'
_API_HEADERS = {
    'Accept': 'application/vnd.api+json',
    'Content-Type': 'application/vnd.api+json',
}
_TIMEOUT_SECONDS = 15

# Maps Lemon Squeezy subscription event names to entitlement statuses.
_SUBSCRIPTION_STATUS = {
    'subscription_created': 'active',
    'subscription_updated': 'active',
    'subscription_resumed': 'active',
    'subscription_unpaused': 'active',
    'subscription_payment_success': 'active',
    'subscription_cancelled': 'canceled',
    'subscription_expired': 'expired',
    'subscription_paused': 'past_due',
    'subscription_payment_failed': 'past_due',
}


class LemonSqueezyProvider:
    """Billing provider backed by Lemon Squeezy (merchant of record)."""

    name = 'lemon_squeezy'

    def _api_key(self) -> Optional[str]:
        return current_app.config.get('LEMON_SQUEEZY_API_KEY')

    def _store_id(self) -> Optional[str]:
        return current_app.config.get('LEMON_SQUEEZY_STORE_ID')

    def _webhook_secret(self) -> Optional[str]:
        return current_app.config.get('LEMON_SQUEEZY_WEBHOOK_SECRET')

    def is_configured(self) -> bool:
        """Return True when API key and store id are present."""
        return bool(self._api_key() and self._store_id())

    def _variant_id_for_plan(self, plan: dict) -> Optional[str]:
        """Resolve the configured Lemon Squeezy variant id for a plan."""
        provider_cfg = plan.get('providers', {}).get(self.name, {})
        env_name = provider_cfg.get('variant_env')
        if not env_name:
            return None
        value = current_app.config.get(env_name)
        return str(value) if value else None

    def _variant_to_plan_key(self) -> Dict[str, str]:
        """Build a reverse map of variant id -> plan_key from the catalog."""
        mapping: Dict[str, str] = {}
        for plan_key, plan in PLANS.items():
            variant_id = self._variant_id_for_plan(plan)
            if variant_id:
                mapping[variant_id] = plan_key
        return mapping

    def create_checkout(
        self,
        *,
        user,
        plan_key: str,
        plan: dict,
        amount_cents: Optional[int] = None,
    ) -> str:
        """Create a Lemon Squeezy checkout and return its URL."""
        if not self.is_configured():
            raise ProviderNotConfiguredError('Lemon Squeezy is not configured')

        variant_id = self._variant_id_for_plan(plan)
        if not variant_id:
            raise ProviderNotConfiguredError(
                f'No Lemon Squeezy variant configured for plan {plan_key}'
            )

        frontend_url = current_app.config.get('FRONTEND_URL', '/').rstrip('/')
        attributes: dict = {
            'checkout_data': {
                'custom': {'user_id': str(user.id)},
            },
            'product_options': {
                'redirect_url': f'{frontend_url}/?billing=success',
            },
        }
        if getattr(user, 'email', None):
            attributes['checkout_data']['email'] = user.email
        if amount_cents is not None:
            attributes['custom_price'] = int(amount_cents)

        payload = {
            'data': {
                'type': 'checkouts',
                'attributes': attributes,
                'relationships': {
                    'store': {
                        'data': {'type': 'stores', 'id': str(self._store_id())},
                    },
                    'variant': {
                        'data': {'type': 'variants', 'id': str(variant_id)},
                    },
                },
            }
        }

        headers = dict(_API_HEADERS)
        headers['Authorization'] = f'Bearer {self._api_key()}'
        response = requests.post(
            f'{_API_BASE}/checkouts',
            headers=headers,
            data=json.dumps(payload),
            timeout=_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        body = response.json()
        return body['data']['attributes']['url']

    def verify_webhook(self, raw_body: bytes, headers) -> None:
        """Verify the ``X-Signature`` HMAC-SHA256 header."""
        secret = self._webhook_secret()
        if not secret:
            raise WebhookVerificationError('Webhook secret not configured')

        signature = headers.get('X-Signature', '')
        digest = hmac.new(
            secret.encode('utf-8'), raw_body, hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(digest, signature):
            raise WebhookVerificationError('Invalid webhook signature')

    def parse_webhook(self, raw_body: bytes, headers) -> BillingWebhookResult:
        """Parse a verified Lemon Squeezy webhook into a normalized result."""
        body = json.loads(raw_body.decode('utf-8'))
        meta = body.get('meta', {})
        data = body.get('data', {})
        attributes = data.get('attributes', {})

        event_type = meta.get('event_name') or headers.get('X-Event-Name', '')
        obj_id = str(data.get('id', ''))
        updated_at = attributes.get('updated_at', '')
        event_id = f'{event_type}:{obj_id}:{updated_at}'

        custom = meta.get('custom_data') or {}
        user_id = _safe_int(custom.get('user_id'))

        variant_map = self._variant_to_plan_key()

        if event_type == 'order_created':
            return self._parse_order(
                event_id, event_type, user_id, obj_id, attributes, variant_map
            )
        if event_type in _SUBSCRIPTION_STATUS:
            return self._parse_subscription(
                event_id, event_type, user_id, obj_id, attributes, variant_map
            )

        return BillingWebhookResult(
            event_id=event_id,
            event_type=event_type,
            handled=False,
            user_id=user_id,
            raw=body,
        )

    def _parse_order(
        self, event_id, event_type, user_id, obj_id, attributes, variant_map
    ) -> BillingWebhookResult:
        first_item = attributes.get('first_order_item', {}) or {}
        variant_id = _safe_str(first_item.get('variant_id'))
        plan_key = variant_map.get(variant_id) if variant_id else None
        return BillingWebhookResult(
            event_id=event_id,
            event_type=event_type,
            handled=plan_key is not None,
            user_id=user_id,
            plan_key=plan_key,
            entitlement_status='active',
            amount_cents=_safe_int(attributes.get('total')),
            provider_customer_id=_safe_str(attributes.get('customer_id')),
            provider_reference_id=str(obj_id),
            current_period_end=None,
        )

    def _parse_subscription(
        self, event_id, event_type, user_id, obj_id, attributes, variant_map
    ) -> BillingWebhookResult:
        variant_id = _safe_str(attributes.get('variant_id'))
        plan_key = variant_map.get(variant_id) if variant_id else None
        return BillingWebhookResult(
            event_id=event_id,
            event_type=event_type,
            handled=plan_key is not None,
            user_id=user_id,
            plan_key=plan_key,
            entitlement_status=_SUBSCRIPTION_STATUS.get(event_type),
            amount_cents=None,
            provider_customer_id=_safe_str(attributes.get('customer_id')),
            provider_reference_id=str(obj_id),
            current_period_end=_parse_iso(attributes.get('renews_at')),
        )


def _safe_int(value) -> Optional[int]:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _safe_str(value) -> Optional[str]:
    return str(value) if value is not None else None


def _parse_iso(value) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    except ValueError:
        return None
