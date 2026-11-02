"""Shared cookie Path helpers for APP_BASE_PATH scoping."""

from flask import current_app, Response

ROOT_COOKIE_PATH = '/'
REFRESH_COOKIE_SUBPATH = '/api/auth'


def app_cookie_path() -> str:
    """Return the configured cookie Path (``APP_BASE_PATH`` or ``/``).

    Returns:
        Cookie path with a leading slash and no trailing slash (except root).
    """
    return current_app.config.get('APP_BASE_PATH') or ROOT_COOKIE_PATH


def refresh_cookie_path() -> str:
    """Return Path for the ``refresh_token`` cookie.

    Built from ``APP_BASE_PATH`` so production under a subpath
    (``/vanilla-webapp-framework``) scopes the cookie to
    ``{APP_BASE_PATH}/api/auth``. At the site root this is ``/api/auth``.

    Returns:
        Cookie path including the ``/api/auth`` suffix.
    """
    base = app_cookie_path()
    if base == ROOT_COOKIE_PATH:
        return REFRESH_COOKIE_SUBPATH
    return f'{base.rstrip("/")}{REFRESH_COOKIE_SUBPATH}'


def cookie_secure() -> bool:
    """Return whether cookies should set the Secure flag.

    Returns:
        True in the production profile.
    """
    return current_app.config.get('APP_PROFILE') == 'production'


def expire_cookie(
    response: Response,
    name: str,
    path: str,
    *,
    httponly: bool,
    samesite: str,
) -> None:
    """Expire ``name`` at ``path`` so the browser drops it.

    Args:
        response: Flask response to mutate.
        name: Cookie name.
        path: Cookie Path attribute to expire.
        httponly: HttpOnly flag matching the live cookie.
        samesite: SameSite flag matching the live cookie.
    """
    response.set_cookie(
        name,
        '',
        expires=0,
        httponly=httponly,
        secure=cookie_secure(),
        samesite=samesite,
        path=path,
    )


def expire_legacy_root_cookie(
    response: Response,
    name: str,
    httponly: bool,
    samesite: str = 'Lax',
) -> None:
    """Expire a leftover ``Path=/`` cookie so it cannot shadow a scoped one.

    No-op when cookies are already issued at ``/``.

    Args:
        response: Flask response to mutate.
        name: Cookie name (``auth_token`` or ``csrf_token``).
        httponly: HttpOnly flag matching the scoped cookie.
        samesite: SameSite flag matching the scoped cookie.
    """
    if app_cookie_path() == ROOT_COOKIE_PATH:
        return
    expire_cookie(
        response,
        name,
        ROOT_COOKIE_PATH,
        httponly=httponly,
        samesite=samesite,
    )


def expire_legacy_refresh_cookies(response: Response, name: str) -> None:
    """Expire leftover ``refresh_token`` cookies at unscoped paths.

    When ``APP_BASE_PATH`` is set, also drops ``Path=/`` and
    ``Path=/api/auth`` copies. No-op for those paths that are the live path.

    Args:
        response: Flask response to mutate.
        name: Cookie name (``refresh_token``).
    """
    current = refresh_cookie_path()
    for path in (ROOT_COOKIE_PATH, REFRESH_COOKIE_SUBPATH):
        if path == current:
            continue
        expire_cookie(
            response,
            name,
            path,
            httponly=True,
            samesite='Strict',
        )
