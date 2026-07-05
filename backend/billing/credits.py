"""In-app credit balance helpers (budget top-ups and spends).

Balance is the sum of ledger deltas. Top-ups (positive) are keyed by the
provider order id to prevent double-credit on webhook redelivery. Fork feature
code spends credits via :func:`spend_credits`.
"""
from typing import Optional

from sqlalchemy import func

from ..db_repository.database import db_session
from ..models.billing_credit_ledger import BillingCreditLedger

INTERNAL_PROVIDER = 'internal'


def get_credit_balance_cents(user_id: int) -> int:
    """Return the user's current credit balance in cents."""
    total = (
        db_session.query(func.coalesce(func.sum(BillingCreditLedger.delta_cents), 0))
        .filter(BillingCreditLedger.user_id == user_id)
        .scalar()
    )
    return int(total or 0)


def add_credits(
    *,
    user_id: int,
    delta_cents: int,
    provider: str,
    provider_reference_id: str,
    plan_key: Optional[str] = None,
) -> bool:
    """Append a positive credit top-up, guarding against duplicates.

    Args:
        user_id: The user receiving credits.
        delta_cents: Positive amount to add.
        provider: Source provider key.
        provider_reference_id: Provider order id (idempotency guard).
        plan_key: Plan/pack that produced the credit, when applicable.

    Returns:
        True if a new row was created, False if the reference already existed.
    """
    existing = BillingCreditLedger.query.filter_by(
        provider=provider, provider_reference_id=provider_reference_id
    ).first()
    if existing is not None:
        return False

    db_session.add(
        BillingCreditLedger(
            user_id=user_id,
            plan_key=plan_key,
            delta_cents=int(delta_cents),
            provider=provider,
            provider_reference_id=provider_reference_id,
        )
    )
    return True


def spend_credits(user_id: int, amount_cents: int) -> bool:
    """Spend credits by appending a negative ledger entry.

    Args:
        user_id: The spending user.
        amount_cents: Positive amount to deduct.

    Returns:
        True when the spend was recorded, False if the balance is insufficient.
    """
    if amount_cents <= 0:
        return False
    if get_credit_balance_cents(user_id) < amount_cents:
        return False

    db_session.add(
        BillingCreditLedger(
            user_id=user_id,
            plan_key=None,
            delta_cents=-int(amount_cents),
            provider=INTERNAL_PROVIDER,
            provider_reference_id=None,
        )
    )
    return True
