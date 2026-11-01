"""Shared cookie Path helpers for APP_BASE_PATH scoping."""
from flask import current_app, Response

ROOT_COOKIE_PATH = '/'


def app_cookie_path() -> str:
    """Return the configured cookie Path (``APP_BASE_PATH`` or ``/``).

    Returns:
        Cookie path with a leading slash and no trailing slash (except root).
    """
    return current_app.config.get('APP_BASE_PATH') or ROOT_COOKIE_PATH


def cookie_secure() -> bool:
    """Return whether cookies should set the Secure flag.

    Returns:
        True in the production profile.
    """
    return current_app.config.get('APP_PROFILE') == 'production'


def expire_legacy_root_cookie(
    response: Response,
    name: str,
    httponly: bool,
) -> None:
    """Expire a leftover ``Path=/`` cookie so it cannot shadow a scoped one.

    No-op when cookies are already issued at ``/``.

    Args:
        response: Flask response to mutate.
        name: Cookie name (``auth_token`` or ``csrf_token``).
        httponly: HttpOnly flag matching the scoped cookie.
    """
    if app_cookie_path() == ROOT_COOKIE_PATH:
        return
    response.set_cookie(
        name,
        '',
        expires=0,
        httponly=httponly,
        secure=cookie_secure(),
        samesite='Lax',
        path=ROOT_COOKIE_PATH,
    )
