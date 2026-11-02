"""SQLAlchemy model for hashed rotating refresh tokens."""

from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from ..db_repository.database import db

_Base: Any = db.Base


class RefreshToken(_Base):
    """One refresh-token version in a rotation family.

    The raw token is never stored. ``token_hash`` is SHA-256 hex of the
    opaque value sent in the ``refresh_token`` cookie.

    Attributes:
        id: Primary key.
        user_id: Owning user (FK ``users.id``).
        family_id: Rotation family (JWT ``sid``) shared by successive replacements.
        token_hash: Unique SHA-256 hex digest of the cookie value.
        token_version: ``users.token_version`` at issue time.
        created_at: When this row was issued.
        expires_at: When this token stops being acceptable.
        family_expires_at: Absolute cap for the family (30 days from login).
        used_at: Set when the token is rotated; reuse after the grace
            window revokes the family.
        revoked_at: Set when the family or this row is revoked.
        user_agent: Truncated User-Agent at issue time.
    """

    __tablename__ = 'refresh_tokens'
    __table_args__ = (
        UniqueConstraint('token_hash', name='uq_refresh_tokens_token_hash'),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    family_id = Column(String(36), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False)
    token_version = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    family_expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    user_agent = Column(String(512), nullable=True)

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f'<RefreshToken user={self.user_id} family={self.family_id} id={self.id}>'
        )
