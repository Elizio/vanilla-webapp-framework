"""Billing entitlement model: a user's feature-access grant per plan/provider."""
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


class BillingEntitlement(db.Base):
    """Access a user holds for a plan, sourced from a billing provider.

    The unique constraint on ``(user_id, plan_key, provider)`` lets the same
    user keep parallel grants across providers (e.g. Lemon Squeezy and Stripe)
    during a future provider migration.

    Attributes:
        id (int): Primary key.
        user_id (int): Owning user (FK ``users.id``).
        plan_key (str): Stable application plan id (e.g. ``supporter``).
        status (str): ``active``, ``canceled``, ``expired`` or ``past_due``.
        provider (str): Source provider key (e.g. ``lemon_squeezy``).
        provider_customer_id (str): Provider customer id, when available.
        provider_reference_id (str): Order or subscription id at the provider.
        current_period_end (datetime): Subscription expiry; null for one-time.
        created_at (datetime): Row creation timestamp.
        updated_at (datetime): Last update timestamp.
    """

    __tablename__ = 'billing_entitlements'
    __table_args__ = (
        UniqueConstraint(
            'user_id', 'plan_key', 'provider', name='uq_entitlement'
        ),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    plan_key = Column(String(64), nullable=False)
    status = Column(String(20), nullable=False, default='active')
    provider = Column(String(32), nullable=False)
    provider_customer_id = Column(String(128), nullable=True)
    provider_reference_id = Column(String(128), nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def __repr__(self) -> str:
        """String representation of the entitlement."""
        return (
            f'<BillingEntitlement user={self.user_id} '
            f'plan={self.plan_key} status={self.status}>'
        )
