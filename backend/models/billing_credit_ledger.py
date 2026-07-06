"""Billing credit ledger model: append-only in-app budget entries."""
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)

from ..db_repository.database import db


class BillingCreditLedger(db.Base):
    """An append-only credit movement for a user's in-app balance.

    Balance is the sum of ``delta_cents`` for a user. Top-ups insert positive
    deltas (keyed by provider order id to prevent double-credit); fork feature
    code inserts negative deltas to spend credits.

    Attributes:
        id (int): Primary key.
        user_id (int): Owning user (FK ``users.id``).
        plan_key (str): Plan/pack that produced the movement, when applicable.
        delta_cents (int): Signed amount added (+) or spent (-).
        provider (str): Source key (e.g. ``lemon_squeezy`` or ``internal``).
        provider_reference_id (str): Provider order id for top-ups; null
            for internal spends. Unique with ``provider`` to guard top-ups.
        created_at (datetime): Row creation timestamp.
    """

    __tablename__ = 'billing_credit_ledger'
    __table_args__ = (
        UniqueConstraint(
            'provider', 'provider_reference_id', name='uq_credit_ref'
        ),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    plan_key = Column(String(64), nullable=True)
    delta_cents = Column(Integer, nullable=False)
    provider = Column(String(32), nullable=False)
    provider_reference_id = Column(String(128), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of the ledger entry."""
        return (
            f'<BillingCreditLedger user={self.user_id} '
            f'delta={self.delta_cents}>'
        )
