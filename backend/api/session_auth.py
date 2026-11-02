"""HttpOnly cookie helpers for JWT session authentication."""

from flask import request

from ..models.user import User
from .cookie_path import (
    app_cookie_path,
    cookie_secure,
    expire_cookie,
    expire_legacy_refresh_cookies,
    expire_legacy_root_cookie,
    refresh_cookie_path,
)
from .csrf import CSRF_COOKIE_NAME
from .jwt_utils import access_token_ttl_seconds, generate_token
from .refresh_tokens import (
    REFRESH_COOKIE_NAME,
    issue_refresh_token,
)

AUTH_COOKIE_NAME = 'auth_token'


def set_auth_cookie(response, user_id: int, token_version: int = 0):
    """Attach a signed JWT as an httpOnly session cookie.

    Also expires any leftover ``Path=/`` ``auth_token`` or ``csrf_token``
    so a stale root-path cookie cannot shadow the scoped one.

    Args:
        response: Flask response to mutate.
        user_id: Authenticated user primary key.
        token_version: Current ``users.token_version`` embedded as claim ``tv``.

    Returns:
        The same response with ``Set-Cookie`` applied.
    """
    token = generate_token(user_id, token_version)
    response.set_cookie(
        AUTH_COOKIE_NAME,
        token,
        httponly=True,
        secure=cookie_secure(),
        samesite='Lax',
        path=app_cookie_path(),
        max_age=access_token_ttl_seconds(),
    )
    expire_legacy_root_cookie(response, AUTH_COOKIE_NAME, httponly=True)
    expire_legacy_root_cookie(response, CSRF_COOKIE_NAME, httponly=True)
    return response


def set_refresh_cookie(response, raw_token: str, max_age: int | None):
    """Attach the opaque refresh token as an httpOnly cookie.

    Path is ``{APP_BASE_PATH}/api/auth`` so login at ``/api/login`` does
    not send it, but ``/api/auth/refresh`` and ``/api/auth/logout`` do.
    SameSite=Strict: only same-site fetches send it. Secure in production.

    Args:
        response: Flask response to mutate.
        raw_token: Opaque token (stored hashed server-side).
        max_age: Seconds for a persistent cookie, or ``None`` for a
            browser-session cookie.

    Returns:
        The same response with ``Set-Cookie`` applied.
    """
    kwargs = {
        'httponly': True,
        'secure': cookie_secure(),
        'samesite': 'Strict',
        'path': refresh_cookie_path(),
    }
    if max_age is not None:
        kwargs['max_age'] = max_age
    response.set_cookie(REFRESH_COOKIE_NAME, raw_token, **kwargs)
    expire_legacy_refresh_cookies(response, REFRESH_COOKIE_NAME)
    return response


def set_session_cookies(response, user: User, *, remember_me: bool = False):
    """Set access and refresh cookies for a newly authenticated user.

    Args:
        response: Flask response to mutate.
        user: Authenticated user row.
        remember_me: Persistent refresh cookie (30-day family cap). OAuth
            logins pass ``True``.

    Returns:
        The same response with both cookies set.
    """
    set_auth_cookie(response, user.id, int(user.token_version or 0))
    raw, max_age = issue_refresh_token(
        user,
        remember_me=remember_me,
        user_agent=request.headers.get('User-Agent'),
    )
    set_refresh_cookie(response, raw, max_age)
    return response


def apply_rotated_refresh(response, user: User, raw_token: str, max_age: int | None):
    """Replace access and refresh cookies after a successful rotation.

    Args:
        response: Flask response to mutate.
        user: Authenticated user row.
        raw_token: Newly issued opaque refresh token.
        max_age: Cookie Max-Age, or ``None`` for a session cookie.

    Returns:
        The same response with both cookies set.
    """
    set_auth_cookie(response, user.id, int(user.token_version or 0))
    set_refresh_cookie(response, raw_token, max_age)
    return response


def clear_refresh_cookie(response):
    """Expire the refresh cookie at its live path and leftover paths.

    Args:
        response: Flask response to mutate.

    Returns:
        The same response.
    """
    expire_cookie(
        response,
        REFRESH_COOKIE_NAME,
        refresh_cookie_path(),
        httponly=True,
        samesite='Strict',
    )
    expire_legacy_refresh_cookies(response, REFRESH_COOKIE_NAME)
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


def clear_session_cookies(response):
    """Clear access and refresh cookies (and leftover Path=/ copies).

    Does not clear ``auth_device``.

    Args:
        response: Flask response to mutate.

    Returns:
        The same response.
    """
    clear_auth_cookie(response)
    clear_refresh_cookie(response)
    return response


def get_refresh_token_from_request() -> str | None:
    """Read the refresh cookie. Refresh tokens in headers are ignored."""
    token = request.cookies.get(REFRESH_COOKIE_NAME)
    if isinstance(token, str) and token:
        return token
    return None


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
