"""Tests for OAuth social login endpoints."""
import pytest

from ..models.user import User
from ..api.oauth import register_oauth_clients
from ..api.session_auth import AUTH_COOKIE_NAME


@pytest.fixture
def oauth_client(test_app, test_db):
    """Test client with Google OAuth configured."""
    test_app.config['GOOGLE_CLIENT_ID'] = 'test-google-id'
    test_app.config['GOOGLE_CLIENT_SECRET'] = 'test-google-secret'
    test_app.config['OAUTH_REDIRECT_BASE'] = 'http://localhost'
    test_app.config['FRONTEND_URL'] = 'http://localhost'
    register_oauth_clients(test_app)
    return test_app.test_client()


def _clear_oauth_config(app):
    """Disable all OAuth providers for isolated tests."""
    app.config['GOOGLE_CLIENT_ID'] = ''
    app.config['GOOGLE_CLIENT_SECRET'] = ''
    app.config['FACEBOOK_CLIENT_ID'] = ''
    app.config['FACEBOOK_CLIENT_SECRET'] = ''
    register_oauth_clients(app)


def test_list_providers_empty(test_app, test_client, test_db):
    _clear_oauth_config(test_app)
    response = test_client.get('/api/auth/providers')
    assert response.status_code == 200
    assert response.json == []


def test_list_providers_with_google(oauth_client):
    response = oauth_client.get('/api/auth/providers')
    assert response.status_code == 200
    assert 'google' in response.json


def test_oauth_login_redirects(oauth_client, monkeypatch):
    from flask import redirect
    from backend.api import oauth as oauth_module

    class FakeClient:
        def authorize_redirect(self, redirect_uri):
            return redirect('https://accounts.google.com/o/oauth2/v2/auth')

    monkeypatch.setattr(
        oauth_module.oauth,
        'create_client',
        lambda _provider: FakeClient(),
    )

    response = oauth_client.get('/api/auth/google/login')
    assert response.status_code == 302
    assert 'accounts.google.com' in response.location


def test_oauth_login_unknown_provider(test_app, test_client, test_db):
    _clear_oauth_config(test_app)
    response = test_client.get('/api/auth/google/login')
    assert response.status_code == 404


def test_oauth_callback_creates_user(oauth_client, monkeypatch):
    from backend.api import oauth as oauth_module

    class FakeClient:
        def authorize_access_token(self):
            return {'access_token': 'fake'}

    monkeypatch.setattr(
        oauth_module.oauth,
        'create_client',
        lambda _provider: FakeClient(),
    )
    monkeypatch.setattr(
        oauth_module,
        '_fetch_userinfo',
        lambda _client, _provider, _token: {
            'oauth_id': 'oauth-123',
            'email': 'social@test.com',
            'name': 'Social User',
        },
    )

    first = oauth_client.get('/api/auth/google/callback?code=fake1')
    second = oauth_client.get('/api/auth/google/callback?code=fake2')
    assert first.status_code == 302
    assert second.status_code == 302
    assert 'auth=success' in first.location
    assert AUTH_COOKIE_NAME in first.headers.getlist('Set-Cookie')[0]

    user = User.query.filter_by(oauth_provider='google', oauth_id='oauth-123').first()
    assert user is not None
    assert user.email == 'social@test.com'
    assert user.password_hash is None

    session = oauth_client.get('/api/auth/session')
    assert session.json['authenticated'] is True
    assert session.json['username'] == user.username


def test_oauth_callback_error_redirect(oauth_client, monkeypatch):
    from backend.api import oauth as oauth_module

    class FakeClient:
        def authorize_access_token(self):
            raise RuntimeError('token exchange failed')

    monkeypatch.setattr(
        oauth_module.oauth,
        'create_client',
        lambda _provider: FakeClient(),
    )

    response = oauth_client.get('/api/auth/google/callback?code=fake')
    assert response.status_code == 302
    assert 'auth_error=AUTH_FAILED' in response.location
