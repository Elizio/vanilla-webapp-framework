"""Shared JWT helpers for password and OAuth login."""

from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app

JWT_ALGORITHM = 'HS256'
DEFAULT_ACCESS_TOKEN_TTL_SECONDS = 900
# Backward-compatible alias used by session cookie max_age.
JWT_EXPIRATION = DEFAULT_ACCESS_TOKEN_TTL_SECONDS


def _jwt_secret():
    key = current_app.config.get('JWT_SECRET_KEY')
    return key or current_app.config.get('JWT_SECRET')


def access_token_ttl_seconds() -> int:
    """Return the access-token lifetime in seconds.

    Returns:
        ``ACCESS_TOKEN_TTL_SECONDS`` from config, default 900.
    """
    raw = current_app.config.get('ACCESS_TOKEN_TTL_SECONDS')
    if raw is None or raw == '':
        return DEFAULT_ACCESS_TOKEN_TTL_SECONDS
    return int(raw)


def token_version_from_payload(payload: dict) -> int | None:
    """Return the JWT ``tv`` claim.

    A missing ``tv`` is treated as ``0`` so tokens minted before this claim
    stay valid against ``users.token_version = 0``. A non-int ``tv`` is
    invalid (``None``).

    Args:
        payload: Decoded JWT claims.

    Returns:
        The integer token version, or ``None`` when ``tv`` is the wrong type.
    """
    if 'tv' not in payload:
        return 0
    token_version = payload['tv']
    if isinstance(token_version, int) and not isinstance(token_version, bool):
        return token_version
    return None


def token_version_matches(payload: dict, token_version: int) -> bool:
    """Return True when the JWT ``tv`` claim matches ``token_version``.

    Args:
        payload: Decoded JWT claims.
        token_version: Current ``users.token_version`` value.

    Returns:
        ``False`` when ``tv`` is missing-invalid or does not match.
    """
    claimed = token_version_from_payload(payload)
    if claimed is None:
        return False
    return claimed == int(token_version)


def generate_token(user_id: int, token_version: int = 0) -> str:
    """Return a signed JWT for the given user id and token version.

    Args:
        user_id: Authenticated user primary key.
        token_version: Current ``users.token_version`` (claim ``tv``).

    Returns:
        Encoded HS256 JWT with ``iat``, ``exp``, ``user_id``, and ``tv``.
    """
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            'user_id': user_id,
            'tv': int(token_version),
            'iat': now,
            'exp': now + timedelta(seconds=access_token_ttl_seconds()),
        },
        _jwt_secret(),
        algorithm=JWT_ALGORITHM,
    )
