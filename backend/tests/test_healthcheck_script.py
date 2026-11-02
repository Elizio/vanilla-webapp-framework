"""Tests for the container HEALTHCHECK helper and stdlib package shadows."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from backend.container_healthcheck import healthcheck_url

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / 'backend'
HEALTHCHECK_SCRIPT = BACKEND_DIR / 'container_healthcheck.py'


def test_healthcheck_url_defaults():
    """Default probe is http://127.0.0.1:5000/api/health."""
    assert healthcheck_url(port='5000', path='/api/health') == (
        'http://127.0.0.1:5000/api/health'
    )


def test_healthcheck_url_respects_port_and_path(monkeypatch):
    """PORT and HEALTHCHECK_PATH from the environment must be honoured."""
    monkeypatch.setenv('PORT', '8080')
    monkeypatch.setenv('HEALTHCHECK_PATH', 'readyz')
    assert healthcheck_url() == 'http://127.0.0.1:8080/readyz'


def test_healthcheck_script_by_path_exits_zero() -> None:
    """Docker runs this file by path; that must not raise ImportError.

    ``python /app/backend/container_healthcheck.py`` puts ``backend/`` at
    ``sys.path[0]``, so a package named ``email`` would shadow stdlib
    ``email`` and break ``import urllib.request``.
    """

    class _OkHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'ok')

        def log_message(self, _format: str, *_args: object) -> None:
            return

    server = HTTPServer(('127.0.0.1', 0), _OkHandler)
    port = int(server.server_address[1])
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    env = os.environ.copy()
    env['PORT'] = str(port)
    env['HEALTHCHECK_PATH'] = '/api/health'
    try:
        result = subprocess.run(
            [sys.executable, str(HEALTHCHECK_SCRIPT)],
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    finally:
        server.shutdown()
        server.server_close()
    combined = f'{result.stdout}{result.stderr}'
    assert result.returncode == 0, combined
    assert 'ImportError' not in combined
    assert 'ModuleNotFoundError' not in combined


def test_backend_packages_do_not_shadow_stdlib() -> None:
    """Top-level packages under backend/ must not reuse stdlib module names."""
    shadowed = sorted(
        child.name
        for child in BACKEND_DIR.iterdir()
        if child.is_dir()
        and (child / '__init__.py').is_file()
        and child.name in sys.stdlib_module_names
    )
    assert shadowed == [], (
        'backend/ packages shadow stdlib modules (HEALTHCHECK puts '
        f'backend/ on sys.path[0]): {shadowed}'
    )
