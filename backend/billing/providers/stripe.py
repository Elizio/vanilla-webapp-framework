"""Stripe billing adapter — migration target stub (not yet implemented).

This documents the future migration path described in the billing design. To
enable Stripe later:

1. Add the ``stripe`` dependency and set ``STRIPE_SECRET_KEY`` /
   ``STRIPE_WEBHOOK_SECRET`` plus per-plan ``price_id`` env vars.
2. Implement :meth:`create_checkout` using a Stripe Checkout Session, passing
   ``client_reference_id=user.id`` (or ``metadata``) so the webhook can resolve
   the user. Return ``session.url``.
3. Implement :meth:`verify_webhook` with ``stripe.Webhook.construct_event`` and
   :meth:`parse_webhook` mapping these events to
   :class:`~backend.billing.providers.base.BillingWebhookResult`:
     - ``checkout.session.completed`` -> grant entitlement / add credits
     - ``invoice.paid`` -> extend ``current_period_end``
     - ``customer.subscription.deleted`` -> status ``canceled``
     - ``invoice.payment_failed`` -> status ``past_due``
4. Add a ``POST /api/billing/webhook/stripe`` route and set
   ``BILLING_PROVIDER=stripe``.

The entitlements/credits tables and feature gates stay unchanged.
"""
from typing import Optional

from .base import BillingWebhookResult


class StripeProvider:
    """Placeholder Stripe adapter. See module docstring for the plan."""

    name = 'stripe'

    def is_configured(self) -> bool:
        """Stripe is not implemented yet."""
        return False

    def create_checkout(
        self,
        *,
        user,
        plan_key: str,
        plan: dict,
        amount_cents: Optional[int] = None,
    ) -> str:
        """Not implemented — see module docstring for the migration steps."""
        raise NotImplementedError('StripeProvider.create_checkout is a stub')

    def verify_webhook(self, raw_body: bytes, headers) -> None:
        """Not implemented — see module docstring for the migration steps."""
        raise NotImplementedError('StripeProvider.verify_webhook is a stub')

    def parse_webhook(self, raw_body: bytes, headers) -> BillingWebhookResult:
        """Not implemented — see module docstring for the migration steps."""
        raise NotImplementedError('StripeProvider.parse_webhook is a stub')
