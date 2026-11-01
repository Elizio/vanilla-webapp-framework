"""Unit tests for the container HEALTHCHECK helper."""
from backend.container_healthcheck import healthcheck_url


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
