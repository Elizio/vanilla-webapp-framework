"""
CORS configuration tests.
"""

from unittest.mock import patch

import pytest
from backend import create_app
from backend.config.app_config import reset_app_config_for_tests


def _cors_app(monkeypatch, **env):
    """Create a test app after resetting config for the given env."""
    for key, value in env.items():
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)
    monkeypatch.setenv('APP_PROFILE', 'testing')
    reset_app_config_for_tests()
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def cors_test_app(monkeypatch):
    """Create a test app with specific CORS configuration."""
    return _cors_app(
        monkeypatch,
        CORS_ORIGINS='http://allowed.example.com,https://allowed.example.com',
    )


@pytest.fixture
def cors_client(cors_test_app, test_db):
    """Test client with CORS configuration."""
    return cors_test_app.test_client()


def test_cors_allowed_origin(cors_client):
    """Test that allowed origins receive proper CORS headers with credentials."""
    response = cors_client.get(
        "/api/public", headers={"Origin": "http://allowed.example.com"}
    )

    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" in response.headers
    assert (
        response.headers["Access-Control-Allow-Origin"] == "http://allowed.example.com"
    )
    assert "Access-Control-Allow-Credentials" in response.headers
    assert response.headers["Access-Control-Allow-Credentials"] == "true"


def test_cors_allowed_origin_https(cors_client):
    """Test that allowed HTTPS origins receive proper CORS headers."""
    response = cors_client.get(
        "/api/public", headers={"Origin": "https://allowed.example.com"}
    )

    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" in response.headers
    assert (
        response.headers["Access-Control-Allow-Origin"] == "https://allowed.example.com"
    )
    assert "Access-Control-Allow-Credentials" in response.headers
    assert response.headers["Access-Control-Allow-Credentials"] == "true"


def test_cors_disallowed_origin(cors_client):
    """Test that disallowed origins do not receive CORS headers."""
    response = cors_client.get(
        "/api/public", headers={"Origin": "http://malicious.example.com"}
    )

    assert response.status_code == 200
    # flask-cors 6.0: disallowed origins must not get CORS headers at all
    assert "Access-Control-Allow-Origin" not in response.headers
    assert "Access-Control-Allow-Credentials" not in response.headers


def test_cors_preflight_allowed(cors_client):
    """Test CORS preflight request for allowed origin."""
    response = cors_client.options(
        "/api/public",
        headers={
            "Origin": "http://allowed.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" in response.headers
    assert (
        response.headers["Access-Control-Allow-Origin"] == "http://allowed.example.com"
    )


def test_cors_preflight_disallowed(cors_client):
    """Test CORS preflight request for disallowed origin."""
    response = cors_client.options(
        "/api/public",
        headers={
            "Origin": "http://malicious.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )

    # Preflight must not return CORS headers for disallowed origins
    assert "Access-Control-Allow-Origin" not in response.headers
    assert "Access-Control-Allow-Credentials" not in response.headers


def test_cors_origins_with_path_match_browser_origin(monkeypatch, test_db):
    """A path-bearing CORS_ORIGINS entry is stripped to scheme://host."""
    app = _cors_app(
        monkeypatch,
        CORS_ORIGINS='https://dsfor.fun/vanilla-webapp-framework',
    )
    client = app.test_client()
    response = client.get('/api/public', headers={'Origin': 'https://dsfor.fun'})
    assert response.status_code == 200
    assert response.headers.get('Access-Control-Allow-Origin') == 'https://dsfor.fun'
    assert response.headers.get('Access-Control-Allow-Credentials') == 'true'


def test_cors_preflight_path_bearing_origin(monkeypatch, test_db):
    """Preflight from the host origin succeeds after path stripping."""
    app = _cors_app(
        monkeypatch,
        CORS_ORIGINS='https://dsfor.fun/vanilla-webapp-framework/',
    )
    client = app.test_client()
    response = client.options(
        '/api/public',
        headers={
            'Origin': 'https://dsfor.fun',
            'Access-Control-Request-Method': 'POST',
        },
    )
    assert response.headers.get('Access-Control-Allow-Origin') == 'https://dsfor.fun'


def test_cors_path_bearing_disallowed_origin_has_no_acao(monkeypatch, test_db):
    """A different host still gets no ACAO after path-bearing config."""
    app = _cors_app(
        monkeypatch,
        CORS_ORIGINS='https://dsfor.fun/vanilla-webapp-framework',
    )
    client = app.test_client()
    response = client.get(
        '/api/public',
        headers={'Origin': 'https://evil.example'},
    )
    assert 'Access-Control-Allow-Origin' not in response.headers


def test_frontend_url_path_is_normalized_only_for_cors(monkeypatch, test_db):
    """FRONTEND_URL keeps its path for redirects; CORS uses the origin only."""
    app = _cors_app(
        monkeypatch,
        CORS_ORIGINS=None,
        FRONTEND_URL='https://dsfor.fun/vanilla-webapp-framework',
    )
    assert app.config['FRONTEND_URL'] == ('https://dsfor.fun/vanilla-webapp-framework')
    assert app.config['CORS_ORIGINS'] == ['https://dsfor.fun']
    client = app.test_client()
    response = client.get('/api/public', headers={'Origin': 'https://dsfor.fun'})
    assert response.headers.get('Access-Control-Allow-Origin') == 'https://dsfor.fun'


def test_cors_malformed_entry_errors_clearly(monkeypatch):
    """Entries without a scheme or host raise a clear, secret-free error."""
    monkeypatch.setenv('CORS_ORIGINS', 'not-a-valid-origin')
    monkeypatch.setenv('APP_PROFILE', 'testing')
    with pytest.raises(ValueError, match='CORS_ORIGINS') as exc_info:
        reset_app_config_for_tests()
    message = str(exc_info.value)
    assert 'scheme' in message.lower() or 'origin' in message.lower()
    assert 'FLASK_SECRET' not in message
    assert 'JWT_SECRET' not in message
    monkeypatch.delenv('CORS_ORIGINS', raising=False)
    reset_app_config_for_tests()


def test_cors_warns_once_when_path_stripped(monkeypatch, test_db):
    """Stripping a path logs one warning that names the variable only."""
    with patch('backend.config.url_settings.logger.warning') as warn:
        _cors_app(
            monkeypatch,
            CORS_ORIGINS=(
                'https://dsfor.fun/vanilla-webapp-framework,https://dsfor.fun/other'
            ),
        )
    assert warn.call_count == 1
    message = warn.call_args[0][0] % warn.call_args[0][1:]
    assert 'CORS_ORIGINS' in message
    assert 'vanilla-webapp-framework' not in message
