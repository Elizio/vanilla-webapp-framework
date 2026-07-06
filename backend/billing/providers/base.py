"""Provider-agnostic billing interfaces shared by all adapters."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Protocol, runtime_checkable

from ...models.user import User


@dataclass
class BillingWebhookResult:
    """Normalized outcome of parsing a provider webhook.

    Adapters translate provider-specific payloads into this shape so the
    service layer can apply domain changes without knowing the provider.

    Attributes:
        event_id: Idempotency key unique per provider event.
        event_type: Provider event name (e.g. ``order_created``).
        handled: Whether this event type maps to a domain action.
        user_id: Application user id resolved from the payload, if any.
        plan_key: Application plan id resolved from the payload, if any.
        entitlement_status: Target entitlement status for entitlement plans
            (``active``/``canceled``/``expired``/``past_due``) or ``None``.
        amount_cents: Paid amount in cents, when present.
        provider_customer_id: Provider customer id, when present.
        provider_reference_id: Order or subscription id at the provider.
        current_period_end: Subscription expiry, when applicable.
    """

    event_id: str
    event_type: str
    handled: bool = False
    user_id: Optional[int] = None
    plan_key: Optional[str] = None
    entitlement_status: Optional[str] = None
    amount_cents: Optional[int] = None
    provider_customer_id: Optional[str] = None
    provider_reference_id: Optional[str] = None
    current_period_end: Optional[datetime] = None
    raw: dict = field(default_factory=dict)


class WebhookVerificationError(Exception):
    """Raised when a webhook signature fails verification."""


class ProviderNotConfiguredError(Exception):
    """Raised when a provider is used without required configuration."""


@runtime_checkable
class BillingProvider(Protocol):
    """Contract every billing provider adapter must satisfy."""

    name: str

    def is_configured(self) -> bool:
        """Return whether the provider has the config needed to operate."""
        ...

    def create_checkout(
        self,
        *,
        user: User,
        plan_key: str,
        plan: dict,
        amount_cents: Optional[int] = None,
    ) -> str:
        """Create a hosted checkout and return its URL.

        Args:
            user: The purchasing user (used to link the webhook back).
            plan_key: Application plan id.
            plan: Resolved plan definition from the catalog.
            amount_cents: Custom amount for donation-style plans.

        Returns:
            The provider-hosted checkout URL to redirect the user to.
        """
        ...

    def verify_webhook(self, raw_body: bytes, headers) -> None:
        """Validate webhook authenticity; raise on failure.

        Raises:
            WebhookVerificationError: If the signature is missing or invalid.
        """
        ...

    def parse_webhook(self, raw_body: bytes, headers) -> BillingWebhookResult:
        """Parse a verified webhook into a :class:`BillingWebhookResult`."""
        ...
