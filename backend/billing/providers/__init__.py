"""Billing provider registry and factory."""
from typing import Dict, Optional

from flask import current_app

from .base import BillingProvider
from .lemon_squeezy import LemonSqueezyProvider
from .stripe import StripeProvider

_PROVIDERS: Dict[str, type] = {
    LemonSqueezyProvider.name: LemonSqueezyProvider,
    StripeProvider.name: StripeProvider,
}

_DEFAULT_PROVIDER = LemonSqueezyProvider.name


def get_billing_provider(name: Optional[str] = None) -> BillingProvider:
    """Return a billing provider instance.

    Args:
        name: Provider key; defaults to ``BILLING_PROVIDER`` config or
            ``lemon_squeezy``.

    Returns:
        An instance of the selected provider adapter.

    Raises:
        ValueError: If the requested provider is unknown.
    """
    key = name or current_app.config.get('BILLING_PROVIDER', _DEFAULT_PROVIDER)
    provider_cls = _PROVIDERS.get(key)
    if provider_cls is None:
        raise ValueError(f'Unknown billing provider: {key}')
    return provider_cls()


__all__ = ['get_billing_provider', 'BillingProvider']
