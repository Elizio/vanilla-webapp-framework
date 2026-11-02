"""Hashed, single-use, expiring email verification and password-reset tokens."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import cast

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..db_repository.database import db, db_session
from ..models.auth_token import AuthToken
from ..models.user import User
from .refresh_tokens import utc_now

PURPOSE_VERIFY = 'verify'
PURPOSE_RESET = 'reset'
VERIFY_TTL = timedelta(hours=24)
RESET_TTL = timedelta(hours=1)
SEND_COOLDOWN = timedelta(seconds=60)
SEND_HOUR_WINDOW = timedelta(hours=1)
SEND_HOUR_MAX = 5


def _orm_session() -> Session:
    """Return the thread-local scoped session (safe from the email worker)."""
    return cast(Session, db.session)


def hash_auth_token(raw: str) -> str:
    """Return the SHA-256 hex digest of a raw email-link token.

    Args:
        raw: Opaque token placed in the email URL.

    Returns:
        64-character hex digest.
    """
    return hashlib.sha256(raw.encode('ascii')).hexdigest()


def _ttl_for(purpose: str) -> timedelta:
    if purpose == PURPOSE_RESET:
        return RESET_TTL
    return VERIFY_TTL


def issue_auth_token(user_id: int, purpose: str) -> str:
    """Persist a hashed token and return the raw value for the email link.

    Args:
        user_id: Owning user primary key.
        purpose: ``verify`` or ``reset``.

    Returns:
        URL-safe raw token (32 bytes). Never stored in the clear.
    """
    raw = secrets.token_urlsafe(32)
    now = utc_now()
    row = AuthToken(
        user_id=user_id,
        purpose=purpose,
        token_hash=hash_auth_token(raw),
        expires_at=now + _ttl_for(purpose),
        created_at=now,
    )
    session = _orm_session()
    session.add(row)
    session.commit()
    return raw


def can_send(user_id: int, purpose: str, *, now: datetime | None = None) -> bool:
    """Return whether another email of ``purpose`` may be sent for ``user_id``.

    Enforces at most one send per 60 s and five per hour, counted from
    ``auth_tokens.created_at`` (shared across gunicorn workers).

    Args:
        user_id: Owning user primary key.
        purpose: ``verify`` or ``reset``.
        now: Clock override for tests.

    Returns:
        ``True`` when a new token may be issued.
    """
    clock = now if now is not None else utc_now()
    session = _orm_session()
    recent = (
        session.query(func.count(AuthToken.id))
        .filter(
            AuthToken.user_id == user_id,
            AuthToken.purpose == purpose,
            AuthToken.created_at >= clock - SEND_COOLDOWN,
        )
        .scalar()
    )
    if int(recent or 0) >= 1:
        return False
    hourly = (
        session.query(func.count(AuthToken.id))
        .filter(
            AuthToken.user_id == user_id,
            AuthToken.purpose == purpose,
            AuthToken.created_at >= clock - SEND_HOUR_WINDOW,
        )
        .scalar()
    )
    return int(hourly or 0) < SEND_HOUR_MAX


def consume_auth_token(raw: str, purpose: str) -> User | None:
    """Mark a matching unused, unexpired token used and return its user.

    Consumes with a conditional ``UPDATE ... SET used_at=now WHERE id=...
    AND used_at IS NULL AND expires_at > now`` and requires ``rowcount == 1``,
    so a double consume succeeds only once. For ``reset``, every remaining
    reset token for that user is then marked used. Unknown, reused, expired,
    or wrong-purpose tokens return ``None``.

    Args:
        raw: Opaque token from the request body.
        purpose: Expected purpose.

    Returns:
        The owning user, or ``None`` when the token is not acceptable.
    """
    if not raw:
        return None
    now = utc_now()
    try:
        digest = hash_auth_token(raw)
    except (UnicodeEncodeError, UnicodeError):
        return None
    row = (
        db_session.query(AuthToken)
        .filter_by(token_hash=digest, purpose=purpose)
        .first()
    )
    if row is None:
        return None
    user = cast(User | None, db_session.get(User, int(row.user_id)))
    if user is None:
        return None
    matched = (
        db_session.query(AuthToken)
        .filter(
            AuthToken.id == row.id,
            AuthToken.used_at.is_(None),
            AuthToken.expires_at > now,
        )
        .update({'used_at': now}, synchronize_session='fetch')
    )
    if int(matched or 0) != 1:
        db_session.rollback()
        return None
    if purpose == PURPOSE_RESET:
        (
            db_session.query(AuthToken)
            .filter(
                AuthToken.user_id == row.user_id,
                AuthToken.purpose == PURPOSE_RESET,
                AuthToken.used_at.is_(None),
            )
            .update({AuthToken.used_at: now}, synchronize_session=False)
        )
    db_session.commit()
    return user
