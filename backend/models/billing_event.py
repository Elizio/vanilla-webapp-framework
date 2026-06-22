"""Billing event model: webhook audit log and idempotency guard."""
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from ..db_repository.database import db


class BillingEvent(db.Base):
    """A received provider webhook, stored for audit and de-duplication.

    The unique constraint on ``(provider, provider_event_id)`` ensures a
    redelivered webhook is processed at most once.

    Attributes:
        id (int): Primary key.
        provider (str): Source provider key (e.g. ``lemon_squeezy``).
        provider_event_id (str): Idempotency key derived from the payload.
        event_type (str): Provider event name (e.g. ``order_created``).
        payload_json (str): Raw request body.
        processed_at (datetime): When the event was stored.
    """

    __tablename__ = 'billing_events'
    __table_args__ = (
        UniqueConstraint(
            'provider', 'provider_event_id', name='uq_billing_event'
        ),
    )

    id = Column(Integer, primary_key=True)
    provider = Column(String(32), nullable=False)
    provider_event_id = Column(String(255), nullable=False)
    event_type = Column(String(64), nullable=False)
    payload_json = Column(Text, nullable=True)
    processed_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        """String representation of the billing event."""
        return (
            f'<BillingEvent provider={self.provider} '
            f'type={self.event_type} id={self.provider_event_id}>'
        )
