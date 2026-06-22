"""Billing orchestration: checkout creation and webhook application.

The service is the single entry point used by the API layer. It validates
plans/amounts, delegates provider specifics to the selected adapter, and
applies webhook results to the app's own entitlement and credit tables.
"""
import json
from typing import Optional

from flask import current_app

from ..db_repository.database import db_session
from ..models.billing_event import BillingEvent
from . import credits as credit_helpers
from . import entitlements as entitlement_helpers
from .plans import OUTCOME_CREDITS, OUTCOME_ENTITLEMENT, get_plan
from .providers import get_billing_provider
from .providers.base import BillingWebhookResult


class BillingError(Exception):
    """Base class for billing service errors."""


class InvalidPlanError(BillingError):
    """Raised when a plan key is unknown."""


class InvalidAmountError(BillingError):
    """Raised when a custom amount is missing or below the plan minimum."""


class BillingNotConfiguredError(BillingError):
    """Raised when the active provider is not configured."""


def create_checkout(user, plan_key: str, amount_cents: Optional[int] = None) -> str:
    """Validate inputs and create a hosted checkout URL.

    Args:
        user: The purchasing user.
        plan_key: Application plan id.
        amount_cents: Custom amount (required for ``custom_amount`` plans).

    Returns:
        The provider-hosted checkout URL.

    Raises:
        InvalidPlanError: Unknown plan.
        InvalidAmountError: Missing/too-low amount for a custom-amount plan.
        BillingNotConfiguredError: Provider lacks required configuration.
    """
    plan = get_plan(plan_key)
    if plan is None:
        raise InvalidPlanError(plan_key)

    provider = get_billing_provider()
    if not provider.is_configured():
        raise BillingNotConfiguredError(provider.name)

    resolved_amount: Optional[int] = None
    if plan.get('custom_amount'):
        if amount_cents is None:
            raise InvalidAmountError('amount_cents is required')
        minimum = plan.get('min_amount_cents', 0)
        if amount_cents < minimum:
            raise InvalidAmountError(f'amount below minimum {minimum}')
        resolved_amount = amount_cents

    return provider.create_checkout(
        user=user,
        plan_key=plan_key,
        plan=plan,
        amount_cents=resolved_amount,
    )


def handle_webhook(raw_body: bytes, headers) -> None:
    """Verify, de-duplicate and apply a provider webhook.

    Verification failures propagate as
    :class:`~backend.billing.providers.base.WebhookVerificationError` for the
    API layer to translate into a 400 response.
    """
    provider = get_billing_provider()
    provider.verify_webhook(raw_body, headers)
    result = provider.parse_webhook(raw_body, headers)

    if _already_processed(provider.name, result.event_id):
        return

    _record_event(provider.name, result, raw_body)

    if result.handled and result.user_id is not None and result.plan_key:
        _apply_result(provider.name, result)

    _commit()


def _already_processed(provider_name: str, event_id: str) -> bool:
    return (
        BillingEvent.query.filter_by(
            provider=provider_name, provider_event_id=event_id
        ).first()
        is not None
    )


def _record_event(
    provider_name: str, result: BillingWebhookResult, raw_body: bytes
) -> None:
    db_session.add(
        BillingEvent(
            provider=provider_name,
            provider_event_id=result.event_id,
            event_type=result.event_type,
            payload_json=raw_body.decode('utf-8', errors='replace'),
        )
    )


def _apply_result(provider_name: str, result: BillingWebhookResult) -> None:
    plan = get_plan(result.plan_key) or {}
    outcome = plan.get('outcome')

    if outcome == OUTCOME_ENTITLEMENT and result.entitlement_status:
        entitlement_helpers.upsert_entitlement(
            user_id=result.user_id,
            plan_key=result.plan_key,
            provider=provider_name,
            status=result.entitlement_status,
            provider_customer_id=result.provider_customer_id,
            provider_reference_id=result.provider_reference_id,
            current_period_end=result.current_period_end,
        )
    elif outcome == OUTCOME_CREDITS and result.amount_cents:
        multiplier = plan.get('credits_multiplier', 1)
        credit_helpers.add_credits(
            user_id=result.user_id,
            delta_cents=int(result.amount_cents * multiplier),
            provider=provider_name,
            provider_reference_id=result.provider_reference_id or result.event_id,
            plan_key=result.plan_key,
        )


def _commit() -> None:
    try:
        db_session.commit()
    except Exception as exc:  # pragma: no cover - defensive rollback
        db_session.rollback()
        current_app.logger.error('Billing webhook commit failed: %s', exc)
        raise


def serialize_event_payload(payload_json: Optional[str]) -> dict:
    """Best-effort decode of a stored event payload (for diagnostics)."""
    if not payload_json:
        return {}
    try:
        return json.loads(payload_json)
    except (ValueError, TypeError):
        return {}
