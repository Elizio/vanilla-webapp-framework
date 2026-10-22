"""Tests for ProxyFix middleware with TRUST_PROXY."""


def test_proxy_fix_applied_when_trust_proxy_enabled(monkeypatch):
    """ProxyFix middleware is applied to wsgi_app when TRUST_PROXY=1."""
    monkeypatch.setenv('TRUST_PROXY', '1')
    monkeypatch.setenv('APP_PROFILE', 'testing')

    from ..config.app_config import reset_app_config_for_tests
    reset_app_config_for_tests()

    from .. import create_app
    from werkzeug.middleware.proxy_fix import ProxyFix

    app = create_app()

    # Verify ProxyFix is in the middleware chain
    assert isinstance(app.wsgi_app, ProxyFix)

    # Verify the app still works with proxy headers
    client = app.test_client()
    response = client.get(
        '/api/health',
        headers={
            'X-Forwarded-Proto': 'https',
            'X-Forwarded-Host': 'example.com',
        }
    )
    assert response.status_code == 200


def test_proxy_fix_not_applied_when_trust_proxy_disabled(monkeypatch):
    """ProxyFix middleware is NOT applied when TRUST_PROXY is unset or 0."""
    monkeypatch.setenv('TRUST_PROXY', '0')
    monkeypatch.setenv('APP_PROFILE', 'testing')

    from ..config.app_config import reset_app_config_for_tests
    reset_app_config_for_tests()

    from .. import create_app
    from werkzeug.middleware.proxy_fix import ProxyFix

    app = create_app()

    # Verify ProxyFix is NOT in the middleware chain
    assert not isinstance(app.wsgi_app, ProxyFix)

    # Verify the app still works
    client = app.test_client()
    response = client.get('/api/health')
    assert response.status_code == 200
