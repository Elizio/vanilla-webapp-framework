"""Persisted rate-limit counter rows shared across app workers."""

from typing import Any

from sqlalchemy import Column, Integer, String

from ..db_repository.database import db

_Base: Any = db.Base


class RateLimitCounter(_Base):
    """One fixed window of hits for a rate-limit scope and key.

    Attributes:
        scope: Bucket family (``auth_ip`` or ``login_user``).
        key: SHA-256 hex digest of the logical IP or exact username.
        window_start: Unix epoch seconds at the start of the window.
        hit_count: Hits recorded in this window.
        expires_at: Unix epoch seconds when the window is stale.
    """

    __tablename__ = 'rate_limit_counters'

    scope = Column(String(32), primary_key=True)
    key = Column(String(255), primary_key=True)
    window_start = Column(Integer, primary_key=True)
    hit_count = Column(Integer, nullable=False)
    expires_at = Column(Integer, nullable=False, index=True)

    def __repr__(self) -> str:
        """Return a debug representation."""
        return (
            f'<RateLimitCounter {self.scope}:{self.key} '
            f'window={self.window_start} count={self.hit_count}>'
        )
