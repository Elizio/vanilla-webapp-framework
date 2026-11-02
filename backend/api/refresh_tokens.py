"""Rotating refresh-token store: issue, rotate, reuse detection, revoke."""

from __future__ import annotations

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import cast

from flask import current_app
from sqlalchemy import or_

from ..db_repository.database import db_session
from ..models.refresh_token import RefreshToken
from ..models.user import User

REUSE_GRACE_SECONDS = 30
REFRESH_COOKIE_NAME = 'refresh_token'


def utc_now() -> datetime:
    """Return naive UTC now (matches DateTime columns on other models)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def hash_refresh_token(raw: str) -> str:
    """Return the SHA-256 hex digest of a raw refresh token.

    Args:
        raw: Opaque cookie value.

    Returns:
        64-character hex digest.
    """
    return hashlib.sha256(raw.encode('ascii')).hexdigest()


def _ttl_days() -> int:
    return int(current_app.config.get('REFRESH_TOKEN_TTL_DAYS') or 30)


def _session_hours() -> int:
    return int(current_app.config.get('REFRESH_SESSION_TTL_HOURS') or 24)


def _user_agent_value(user_agent: str | None) -> str | None:
    if not user_agent:
        return None
    trimmed = user_agent.strip()
    if not trimmed:
        return None
    return trimmed[:512]


def _is_persistent(row: RefreshToken) -> bool:
    """Infer remember-me from this row's lifetime vs the family cap."""
    created = cast(datetime, row.created_at)
    expires = cast(datetime, row.expires_at)
    family_expires = cast(datetime, row.family_expires_at)
    lifetime = expires - created
    family_lifetime = family_expires - created
    return lifetime >= family_lifetime - timedelta(hours=1)


def _cookie_max_age(row: RefreshToken, persistent: bool) -> int | None:
    if not persistent:
        return None
    remaining = int((row.expires_at - utc_now()).total_seconds())
    return max(remaining, 0)


def purge_stale_tokens(user_id: int) -> None:
    """Delete expired or revoked refresh rows for one user.

    Used tokens that are still within TTL stay so reuse detection works.

    Args:
        user_id: Owning user primary key.
    """
    now = utc_now()
    db_session.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        or_(
            RefreshToken.expires_at < now,
            RefreshToken.revoked_at.isnot(None),
        ),
    ).delete(synchronize_session=False)
    db_session.commit()


def revoke_family(family_id: str) -> int:
    """Mark every unrevoked row in a family as revoked.

    Args:
        family_id: Rotation family id.

    Returns:
        Number of rows updated.
    """
    now = utc_now()
    count = (
        db_session.query(RefreshToken)
        .filter(
            RefreshToken.family_id == family_id,
            RefreshToken.revoked_at.is_(None),
        )
        .update({'revoked_at': now}, synchronize_session=False)
    )
    db_session.commit()
    return int(count or 0)


def revoke_all_families(user_id: int) -> int:
    """Revoke every refresh family for a user (logout-all).

    Args:
        user_id: Owning user primary key.

    Returns:
        Number of rows updated.
    """
    now = utc_now()
    count = (
        db_session.query(RefreshToken)
        .filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        )
        .update({'revoked_at': now}, synchronize_session=False)
    )
    db_session.commit()
    return int(count or 0)


def revoke_presented_token(raw_token: str) -> None:
    """Revoke the family of a presented refresh cookie, if it exists.

    Args:
        raw_token: Opaque cookie value. Unknown hashes are ignored.
    """
    row = (
        db_session.query(RefreshToken)
        .filter_by(token_hash=hash_refresh_token(raw_token))
        .one_or_none()
    )
    if row is None:
        return
    revoke_family(str(row.family_id))


def _insert_token(
    user: User,
    *,
    family_id: str,
    family_expires_at: datetime,
    persistent: bool,
    user_agent: str | None,
) -> tuple[str, RefreshToken]:
    now = utc_now()
    ttl = (
        timedelta(days=_ttl_days()) if persistent else timedelta(hours=_session_hours())
    )
    expires_at = min(now + ttl, family_expires_at)
    raw = secrets.token_urlsafe(32)
    row = RefreshToken(
        user_id=user.id,
        family_id=family_id,
        token_hash=hash_refresh_token(raw),
        token_version=int(user.token_version or 0),
        created_at=now,
        expires_at=expires_at,
        family_expires_at=family_expires_at,
        user_agent=_user_agent_value(user_agent),
    )
    db_session.add(row)
    db_session.commit()
    return raw, row


def issue_refresh_token(
    user: User,
    *,
    remember_me: bool,
    user_agent: str | None = None,
) -> tuple[str, int | None]:
    """Create a new refresh family for a login and return the cookie value.

    Args:
        user: Authenticated user.
        remember_me: Persistent 30-day cookie when True; session cookie
            with 24 h server TTL when False.
        user_agent: Optional User-Agent to store.

    Returns:
        ``(raw_token, cookie_max_age)``. ``cookie_max_age`` is ``None``
        for a browser-session cookie.
    """
    purge_stale_tokens(int(user.id))
    now = utc_now()
    family_expires_at = now + timedelta(days=_ttl_days())
    raw, row = _insert_token(
        user,
        family_id=str(uuid.uuid4()),
        family_expires_at=family_expires_at,
        persistent=remember_me,
        user_agent=user_agent,
    )
    return raw, _cookie_max_age(row, remember_me)


@dataclass(frozen=True)
class RotatedRefresh:
    """Successful refresh rotation (or grace sibling)."""

    user: User
    raw_token: str
    cookie_max_age: int | None


def rotate_refresh_token(
    raw_token: str,
    *,
    user_agent: str | None = None,
) -> RotatedRefresh | str:
    """Rotate a refresh token or report why it cannot be used.

    Args:
        raw_token: Opaque cookie value.
        user_agent: Optional User-Agent stored on a newly issued row.

    Returns:
        A :class:`RotatedRefresh` on success, or ``'inactive'`` /
        ``'invalid'`` when the caller should 403 / 401.
    """
    now = utc_now()
    token_hash = hash_refresh_token(raw_token)
    row = db_session.query(RefreshToken).filter_by(token_hash=token_hash).one_or_none()
    if row is None:
        return 'invalid'

    user = db_session.get(User, row.user_id)
    if user is None:
        return 'invalid'
    if not bool(user.is_active):
        return 'inactive'
    if int(row.token_version) != int(user.token_version or 0):
        return 'invalid'

    persistent = _is_persistent(row)

    if row.revoked_at is not None:
        return 'invalid'

    if row.used_at is not None:
        used_at = row.used_at
        age = (now - used_at).total_seconds()
        if 0 <= age <= REUSE_GRACE_SECONDS and row.family_expires_at >= now:
            raw, new_row = _insert_token(
                user,
                family_id=str(row.family_id),
                family_expires_at=row.family_expires_at,
                persistent=persistent,
                user_agent=user_agent,
            )
            purge_stale_tokens(int(user.id))
            return RotatedRefresh(
                user=user,
                raw_token=raw,
                cookie_max_age=_cookie_max_age(new_row, persistent),
            )
        current_app.logger.warning(
            'Refresh token reuse detected; family revoked user_id=%s family_id=%s',
            row.user_id,
            row.family_id,
        )
        revoke_family(str(row.family_id))
        return 'invalid'

    if row.expires_at < now or row.family_expires_at < now:
        return 'invalid'

    matched = (
        db_session.query(RefreshToken)
        .filter(
            RefreshToken.id == row.id,
            RefreshToken.used_at.is_(None),
            RefreshToken.revoked_at.is_(None),
        )
        .update({'used_at': now}, synchronize_session='fetch')
    )
    db_session.commit()
    if int(matched or 0) != 1:
        # Lost a same-token race: the winner marked it used. Re-read so
        # the grace window can issue a sibling instead of looping.
        db_session.expire_all()
        return rotate_refresh_token(raw_token, user_agent=user_agent)

    raw, new_row = _insert_token(
        user,
        family_id=str(row.family_id),
        family_expires_at=row.family_expires_at,
        persistent=persistent,
        user_agent=user_agent,
    )
    purge_stale_tokens(int(user.id))
    return RotatedRefresh(
        user=user,
        raw_token=raw,
        cookie_max_age=_cookie_max_age(new_row, persistent),
    )
