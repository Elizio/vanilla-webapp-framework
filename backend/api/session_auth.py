"""HttpOnly cookie helpers for JWT session authentication."""
from flask import request

from .cookie_path import (
    app_cookie_path,
    cookie_secure,
    expire_legacy_root_cookie,
)
from .csrf import CSRF_COOKIE_NAME
from .jwt_utils import JWT_EXPIRATION, generate_token

AUTH_COOKIE_NAME = 'auth_token'


def set_auth_cookie(response, user_id: int):
    """Attach a signed JWT as an httpOnly session cookie.

    Also expires any leftover ``Path=/`` ``auth_token`` or ``csrf_token``
    so a stale root-path cookie cannot shadow the scoped one.

    Args:
        response: Flask response to mutate.
        user_id: Authenticated user primary key.

    Returns:
        The same response with ``Set-Cookie`` applied.
    """
    token = generate_token(user_id)
    response.set_cookie(
        AUTH_COOKIE_NAME,
        token,
        httponly=True,
        secure=cookie_secure(),
        samesite='Lax',
        path=app_cookie_path(),
        max_age=JWT_EXPIRATION,
    )
    expire_legacy_root_cookie(response, AUTH_COOKIE_NAME, httponly=True)
    expire_legacy_root_cookie(response, CSRF_COOKIE_NAME, httponly=True)
    return response


def clear_auth_cookie(response):
    """Remove the session cookie from the client.

    Clears the cookie at ``APP_BASE_PATH`` and expires leftover ``Path=/``
    ``auth_token`` and ``csrf_token`` cookies.

    Args:
        response: Flask response to mutate.

    Returns:
        The same response with clear ``Set-Cookie`` headers applied.
    """
    response.set_cookie(
        AUTH_COOKIE_NAME,
        '',
        expires=0,
        httponly=True,
        secure=cookie_secure(),
        samesite='Lax',
        path=app_cookie_path(),
    )
    expire_legacy_root_cookie(response, AUTH_COOKIE_NAME, httponly=True)
    expire_legacy_root_cookie(response, CSRF_COOKIE_NAME, httponly=True)
    return response


def get_token_from_request() -> str | None:
    """Read JWT from the session cookie or ``Authorization: Bearer`` header."""
    token = request.cookies.get(AUTH_COOKIE_NAME)
    if token:
        return token

    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None

    parts = auth_header.split(' ', 1)
    if len(parts) == 2 and parts[0] == 'Bearer':
        return parts[1]
    return None
