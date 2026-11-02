"""HttpOnly cookie helpers for JWT session authentication."""

from flask import request

from ..models.user import User
from ..config.cookie_names import (
    LEGACY_AUTH_COOKIE_NAME,
    LEGACY_CSRF_COOKIE_NAME,
    LEGACY_REFRESH_COOKIE_NAME,
)
from .cookie_path import (
    app_cookie_path,
    auth_cookie_name,
    cookie_secure,
    csrf_cookie_name,
    expire_cookie,
    expire_legacy_refresh_cookies,
    expire_legacy_root_cookie,
    expire_replaced_cookie,
    expire_replaced_refresh_cookie,
    refresh_cookie_name,
    refresh_cookie_path,
)
from .jwt_utils import access_token_ttl_seconds, generate_token
from .refresh_tokens import issue_refresh_token


def set_auth_cookie(
    response,
    user_id: int,
    token_version: int = 0,
    session_id: str | None = None,
):
    """Attach a signed JWT as an httpOnly session cookie.

    Also expires leftover ``Path=/`` copies of the live names and the
    legacy ``auth_token`` / ``csrf_token`` names so a stale cookie cannot
    shadow the scoped one.

    Args:
        response: Flask response to mutate.
        user_id: Authenticated user primary key.
        token_version: Current ``users.token_version`` embedded as claim ``tv``.
        session_id: Refresh family id embedded as claim ``sid``.

    Returns:
        The same response with ``Set-Cookie`` applied.
    """
    token = generate_token(user_id, token_version, session_id=session_id)
    live_auth = auth_cookie_name()
    live_csrf = csrf_cookie_name()
    response.set_cookie(
        live_auth,
        token,
        httponly=True,
        secure=cookie_secure(),
        samesite='Lax',
        path=app_cookie_path(),
        max_age=access_token_ttl_seconds(),
    )
    expire_legacy_root_cookie(response, live_auth, httponly=True)
    expire_legacy_root_cookie(response, live_csrf, httponly=True)
    if live_auth != LEGACY_AUTH_COOKIE_NAME:
        expire_replaced_cookie(response, LEGACY_AUTH_COOKIE_NAME, httponly=True)
    if live_csrf != LEGACY_CSRF_COOKIE_NAME:
        expire_replaced_cookie(response, LEGACY_CSRF_COOKIE_NAME, httponly=True)
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
    live_refresh = refresh_cookie_name()
    response.set_cookie(live_refresh, raw_token, **kwargs)
    expire_legacy_refresh_cookies(response, live_refresh)
    if live_refresh != LEGACY_REFRESH_COOKIE_NAME:
        expire_replaced_refresh_cookie(response, LEGACY_REFRESH_COOKIE_NAME)
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
    raw, max_age, family_id = issue_refresh_token(
        user,
        remember_me=remember_me,
        user_agent=request.headers.get('User-Agent'),
    )
    set_auth_cookie(
        response,
        user.id,
        int(user.token_version or 0),
        session_id=family_id,
    )
    set_refresh_cookie(response, raw, max_age)
    return response


def apply_rotated_refresh(
    response,
    user: User,
    raw_token: str,
    max_age: int | None,
    family_id: str,
):
    """Replace access and refresh cookies after a successful rotation.

    Args:
        response: Flask response to mutate.
        user: Authenticated user row.
        raw_token: Newly issued opaque refresh token.
        max_age: Cookie Max-Age, or ``None`` for a session cookie.
        family_id: Refresh family id written as JWT ``sid``.

    Returns:
        The same response with both cookies set.
    """
    set_auth_cookie(
        response,
        user.id,
        int(user.token_version or 0),
        session_id=family_id,
    )
    set_refresh_cookie(response, raw_token, max_age)
    return response


def clear_refresh_cookie(response):
    """Expire the refresh cookie at its live path and leftover paths.

    Args:
        response: Flask response to mutate.

    Returns:
        The same response.
    """
    live_refresh = refresh_cookie_name()
    expire_cookie(
        response,
        live_refresh,
        refresh_cookie_path(),
        httponly=True,
        samesite='Strict',
    )
    expire_legacy_refresh_cookies(response, live_refresh)
    expire_replaced_refresh_cookie(response, LEGACY_REFRESH_COOKIE_NAME)
    return response


def clear_auth_cookie(response):
    """Remove the session cookie from the client.

    Clears the cookie at ``APP_BASE_PATH`` and expires leftover ``Path=/``
    copies plus the legacy ``auth_token`` and ``csrf_token`` names.

    Args:
        response: Flask response to mutate.

    Returns:
        The same response with clear ``Set-Cookie`` headers applied.
    """
    live_auth = auth_cookie_name()
    live_csrf = csrf_cookie_name()
    response.set_cookie(
        live_auth,
        '',
        expires=0,
        httponly=True,
        secure=cookie_secure(),
        samesite='Lax',
        path=app_cookie_path(),
    )
    expire_legacy_root_cookie(response, live_auth, httponly=True)
    expire_legacy_root_cookie(response, live_csrf, httponly=True)
    expire_replaced_cookie(response, LEGACY_AUTH_COOKIE_NAME, httponly=True)
    expire_replaced_cookie(response, LEGACY_CSRF_COOKIE_NAME, httponly=True)
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


def _first_cookie(*names: str) -> str | None:
    """Return the first non-empty cookie among ``names`` (live, then legacy).

    Legacy unprefixed names stay readable until ``REFRESH_TOKEN_TTL_DAYS``
    plus 7 days after the namespaced-cookie deploy; keep expiring them.
    """
    for name in names:
        token = request.cookies.get(name)
        if isinstance(token, str) and token:
            return token
    return None


def get_refresh_token_from_request() -> str | None:
    """Read the refresh cookie. Refresh tokens in headers are ignored."""
    return _first_cookie(refresh_cookie_name(), LEGACY_REFRESH_COOKIE_NAME)


def get_token_from_request() -> str | None:
    """Read JWT from the session cookie or ``Authorization: Bearer`` header."""
    token = _first_cookie(auth_cookie_name(), LEGACY_AUTH_COOKIE_NAME)
    if token:
        return token

    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None

    parts = auth_header.split(' ', 1)
    if len(parts) == 2 and parts[0] == 'Bearer':
        return parts[1]
    return None
