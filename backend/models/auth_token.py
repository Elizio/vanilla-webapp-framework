"""SQLAlchemy model for hashed email-verification and password-reset tokens."""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from ..db_repository.database import db

_Base: Any = db.Base


class AuthToken(_Base):
    """One single-use verification or reset token.

    The raw token is never stored. ``token_hash`` is SHA-256 hex of the
    value placed in the email link.

    Attributes:
        id: Primary key.
        user_id: Owning user (FK ``users.id``).
        purpose: ``verify`` or ``reset``.
        token_hash: Unique SHA-256 hex digest of the raw token.
        expires_at: When the token stops being acceptable.
        used_at: Set when consumed; reuse returns invalid.
        created_at: Issue time (per-address send cooldown).
    """

    __tablename__ = 'auth_tokens'
    __table_args__ = (UniqueConstraint('token_hash', name='uq_auth_tokens_token_hash'),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    purpose = Column(String(16), nullable=False)
    token_hash = Column(String(64), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self) -> str:
        """Return a debug representation."""
        return f'<AuthToken user={self.user_id} purpose={self.purpose} id={self.id}>'
