"""
CORS configuration tests.
"""

import pytest
from backend import create_app


@pytest.fixture
def cors_test_app(monkeypatch):
    """Create a test app with specific CORS configuration."""
    # Set CORS_ORIGINS before app creation
    monkeypatch.setenv(
        "CORS_ORIGINS", "http://allowed.example.com,https://allowed.example.com"
    )

    # Clear cached config instance to force reload
    from backend.config.app_config import AppConfig

    AppConfig._instance = None

    app = create_app()
    app.config["TESTING"] = True

    return app


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
