"""Namespaced HttpOnly cookie names derived from COOKIE_PREFIX.

COOKIE_PREFIX defaults to a slug of APP_NAME. Changing COOKIE_PREFIX (or
APP_NAME, when COOKIE_PREFIX is unset) issues new cookie names and logs
everyone out.

Legacy unprefixed names (``csrf_token``, ``auth_token``, ``refresh_token``,
``auth_device``) stay readable so current sessions survive the rename.
Remove those reads after ``REFRESH_TOKEN_TTL_DAYS`` plus 7 days from the
namespaced-cookie deploy. Keep expiring the old names whenever a live
cookie is issued or cleared.
"""

from __future__ import annotations

import re

DEFAULT_COOKIE_PREFIX = 'vanilla-webapp-framework'
LEGACY_CSRF_COOKIE_NAME = 'csrf_token'
LEGACY_AUTH_COOKIE_NAME = 'auth_token'
LEGACY_REFRESH_COOKIE_NAME = 'refresh_token'
LEGACY_DEVICE_COOKIE_NAME = 'auth_device'

_UNSAFE_COOKIE_CHARS = re.compile(r'[^a-z0-9]+')


def slug_cookie_prefix(value: str | None) -> str:
    """Return a cookie-safe slug, never blank or leading-underscore.

    Args:
        value: Raw APP_NAME or COOKIE_PREFIX, or ``None``.

    Returns:
        Lowercase hyphenated prefix with at least one alphanumeric.
    """
    slug = _UNSAFE_COOKIE_CHARS.sub('-', (value or '').strip().lower())
    slug = slug.strip('-')
    return slug or DEFAULT_COOKIE_PREFIX


def cookie_name_prefix(app_name: str | None) -> str:
    """Return the default cookie prefix slug for ``app_name``.

    Args:
        app_name: Display name from ``APP_NAME``, or ``None``.

    Returns:
        Lowercase hyphenated prefix with at least one alphanumeric.
    """
    return slug_cookie_prefix(app_name)


def resolve_cookie_prefix(cookie_prefix: str | None, app_name: str | None) -> str:
    """Return COOKIE_PREFIX when set, otherwise a slug of APP_NAME.

    Args:
        cookie_prefix: ``COOKIE_PREFIX`` env value.
        app_name: Display name from ``APP_NAME``, or ``None``.

    Returns:
        Cookie-safe prefix used to namespace session cookies.
    """
    raw = (cookie_prefix or '').strip().strip("'\"")
    if raw:
        return slug_cookie_prefix(raw)
    return slug_cookie_prefix(app_name)


def namespaced_cookie_name(prefix: str, suffix: str) -> str:
    """Return ``{prefix}_{suffix}`` for a session cookie.

    Args:
        prefix: Already-resolved COOKIE_PREFIX.
        suffix: Legacy cookie suffix such as ``csrf_token``.

    Returns:
        Namespaced cookie name.
    """
    return f'{prefix}_{suffix}'


def resolve_cookie_name(override: str | None, prefix: str, suffix: str) -> str:
    """Return an explicit override or the namespaced default.

    Args:
        override: ``CSRF_COOKIE_NAME`` (or sibling) env value.
        prefix: Already-resolved COOKIE_PREFIX.
        suffix: Legacy cookie suffix such as ``csrf_token``.

    Returns:
        Override when it is non-empty after stripping; otherwise the
        namespaced default.
    """
    raw = (override or '').strip().strip("'\"")
    if raw:
        return raw
    return namespaced_cookie_name(prefix, suffix)
