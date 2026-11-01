"""Container HEALTHCHECK helper using stdlib urllib (no curl)."""

from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request


def healthcheck_url(
    port: str | None = None,
    path: str | None = None,
) -> str:
    """Build the localhost health URL from PORT and HEALTHCHECK_PATH.

    Args:
        port: Listen port override. Defaults to ``PORT`` or ``5000``.
        path: URL path override. Defaults to ``HEALTHCHECK_PATH`` or
            ``/api/health``. A leading slash is added when missing.

    Returns:
        Absolute URL probed by the Docker HEALTHCHECK.
    """
    resolved_port = port if port is not None else os.environ.get('PORT', '5000')
    resolved_path = (
        path if path is not None else os.environ.get('HEALTHCHECK_PATH', '/api/health')
    )
    if not resolved_path.startswith('/'):
        resolved_path = f'/{resolved_path}'
    return f'http://127.0.0.1:{resolved_port}{resolved_path}'


def main() -> int:
    """GET the health URL; return 0 only on HTTP 200.

    Returns:
        Process exit status for Docker HEALTHCHECK.
    """
    url = healthcheck_url()
    try:
        with urllib.request.urlopen(url, timeout=4) as response:
            return 0 if getattr(response, 'status', 0) == 200 else 1
    except (urllib.error.URLError, OSError):
        return 1


if __name__ == '__main__':
    sys.exit(main())
