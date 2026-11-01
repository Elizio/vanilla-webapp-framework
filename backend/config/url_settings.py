"""Normalize APP_BASE_PATH and browser origins for cookies and CORS."""

from __future__ import annotations

import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def normalize_app_base_path(raw: str | None) -> str:
    """Return a cookie Path value from ``APP_BASE_PATH``.

    Empty or unset becomes ``/``. A relative path gets a leading slash and
    any trailing slash is removed. Values with a scheme, host, query, fragment,
    or ``..`` raise ``ValueError`` without echoing the raw input.

    Args:
        raw: The ``APP_BASE_PATH`` environment value, or ``None``.

    Returns:
        A path starting with ``/`` and with no trailing slash (except root).

    Raises:
        ValueError: If the value is a URL, contains a query, or contains ``..``.
    """
    if raw is None:
        return '/'
    value = raw.strip().strip("'\"")
    if not value:
        return '/'
    if '..' in value:
        raise ValueError('APP_BASE_PATH is invalid: must be a path without ..')
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError(
            'APP_BASE_PATH is invalid: use a path with a leading slash, '
            'and without a scheme, host, or query'
        )
    if not value.startswith('/'):
        value = f'/{value}'
    return value.rstrip('/') or '/'


def normalize_browser_origin(raw: str) -> tuple[str, bool]:
    """Normalize a URL to ``scheme://host[:port]`` for CORS matching.

    Args:
        raw: A configured origin or frontend URL that may include a path.

    Returns:
        A tuple of the origin and whether a path, query, fragment, userinfo,
        or trailing slash was stripped.

    Raises:
        ValueError: If the value has no scheme or host.
    """
    value = raw.strip()
    parsed = urlparse(value)
    host = parsed.hostname
    if not parsed.scheme or not host:
        raise ValueError('origin must include a scheme and host')
    if ':' in host:
        host = f'[{host}]'
    if parsed.port:
        origin = f'{parsed.scheme}://{host}:{parsed.port}'
    else:
        origin = f'{parsed.scheme}://{host}'
    stripped = bool(
        parsed.path not in ('',)
        or parsed.query
        or parsed.fragment
        or parsed.username
        or parsed.password
    )
    return origin, stripped


def parse_cors_origins(cors_raw: str, frontend_url: str) -> list[str]:
    """Parse ``CORS_ORIGINS`` or fall back to the ``FRONTEND_URL`` origin.

    Path-bearing entries are stripped to the browser Origin. One warning is
    emitted per source variable; the warning names the variable and does not
    echo values.

    Args:
        cors_raw: Raw ``CORS_ORIGINS`` env value (comma-separated).
        frontend_url: Full ``FRONTEND_URL`` (may include a path).

    Returns:
        Deduplicated list of ``scheme://host[:port]`` origins.

    Raises:
        ValueError: If an explicit ``CORS_ORIGINS`` entry lacks scheme or host.
    """
    if cors_raw.strip():
        return _origins_from_entries(
            cors_raw.split(','),
            variable_name='CORS_ORIGINS',
            required=True,
        )
    if not frontend_url or frontend_url.strip() in ('', '/'):
        return []
    return _origins_from_entries(
        [frontend_url],
        variable_name='FRONTEND_URL',
        required=False,
    )


def _origins_from_entries(
    entries: list[str],
    variable_name: str,
    required: bool,
) -> list[str]:
    """Normalize origin entries and optionally warn when a path is stripped."""
    origins: list[str] = []
    stripped_any = False
    for item in entries:
        item = item.strip()
        if not item:
            continue
        try:
            origin, stripped = normalize_browser_origin(item)
        except ValueError:
            if required:
                raise ValueError(
                    f'{variable_name} must contain scheme://host[:port] '
                    'origins only (no paths required; entries need a scheme '
                    'and host)'
                ) from None
            continue
        if stripped:
            stripped_any = True
        if origin not in origins:
            origins.append(origin)
    if stripped_any:
        logger.warning(
            '%s included a path or trailing slash; using the origin only',
            variable_name,
        )
    return origins
