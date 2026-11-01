"""Tests for OAuth social login endpoints."""
import pytest

from ..models.user import User
from ..db_repository.database import db_session
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


def _fake_token_client():
    class FakeClient:
        def authorize_access_token(self):
            return {'access_token': 'fake'}

    return FakeClient()


def _patch_oauth_callback(monkeypatch, profile):
    from backend.api import oauth as oauth_module

    monkeypatch.setattr(
        oauth_module.oauth,
        'create_client',
        lambda _provider: _fake_token_client(),
    )
    monkeypatch.setattr(
        oauth_module,
        '_fetch_userinfo',
        lambda _client, _provider, _token: profile,
    )


def test_oauth_callback_inactive_user_redirects_without_session(
    oauth_client, test_db, monkeypatch
):
    """Inactive OAuth users get an error redirect and no session cookie."""
    user = User(
        username='inactiveoauth',
        password_hash=None,
        oauth_provider='google',
        oauth_id='oauth-inactive',
        is_active=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.expunge_all()

    _patch_oauth_callback(
        monkeypatch,
        {
            'oauth_id': 'oauth-inactive',
            'email': 'inactive@test.com',
            'name': 'Inactive',
            'email_verified': True,
        },
    )
    response = oauth_client.get('/api/auth/google/callback?code=fake')
    assert response.status_code == 302
    assert 'auth_error=ACCOUNT_INACTIVE' in response.location
    cookies = response.headers.getlist('Set-Cookie')
    assert not any(AUTH_COOKIE_NAME in cookie for cookie in cookies)
    session = oauth_client.get('/api/auth/session')
    assert session.json['authenticated'] is False


def test_google_verified_email_links_existing_password_account(
    oauth_client, test_db, monkeypatch
):
    existing = User(
        username='localuser',
        email='same@test.com',
        password_hash='hashed',
        oauth_provider=None,
    )
    db_session.add(existing)
    db_session.commit()
    existing_id = existing.id
    db_session.expunge_all()

    _patch_oauth_callback(
        monkeypatch,
        {
            'oauth_id': 'google-sub-1',
            'email': 'same@test.com',
            'name': 'Local User',
            'email_verified': True,
        },
    )
    response = oauth_client.get('/api/auth/google/callback?code=fake')
    assert response.status_code == 302
    assert 'auth=success' in response.location
    linked = User.query.filter_by(
        oauth_provider='google', oauth_id='google-sub-1'
    ).first()
    assert linked is not None
    assert linked.id == existing_id
    assert User.query.filter_by(email='same@test.com').count() == 1


def test_google_unverified_email_does_not_link(oauth_client, test_db, monkeypatch):
    existing = User(
        username='localuser2',
        email='unverified@test.com',
        password_hash='hashed',
        oauth_provider=None,
    )
    db_session.add(existing)
    db_session.commit()
    existing_id = existing.id
    db_session.expunge_all()

    _patch_oauth_callback(
        monkeypatch,
        {
            'oauth_id': 'google-sub-unverified',
            'email': 'unverified@test.com',
            'name': 'Unverified',
            'email_verified': False,
        },
    )
    response = oauth_client.get('/api/auth/google/callback?code=fake')
    assert response.status_code == 302
    assert 'auth=success' in response.location
    created = User.query.filter_by(
        oauth_provider='google', oauth_id='google-sub-unverified'
    ).first()
    assert created is not None
    assert created.id != existing_id
    assert User.query.filter_by(email='unverified@test.com').count() == 2


@pytest.fixture
def facebook_oauth_client(test_app, test_db):
    """Test client with Facebook OAuth configured."""
    test_app.config['FACEBOOK_CLIENT_ID'] = 'test-facebook-id'
    test_app.config['FACEBOOK_CLIENT_SECRET'] = 'test-facebook-secret'
    test_app.config['OAUTH_REDIRECT_BASE'] = 'http://localhost'
    test_app.config['FRONTEND_URL'] = 'http://localhost'
    register_oauth_clients(test_app)
    return test_app.test_client()


def test_facebook_never_links_by_email(
    facebook_oauth_client, test_db, monkeypatch
):
    existing = User(
        username='fblocal',
        email='fb@test.com',
        password_hash='hashed',
        oauth_provider=None,
    )
    db_session.add(existing)
    db_session.commit()
    existing_id = existing.id
    db_session.expunge_all()

    _patch_oauth_callback(
        monkeypatch,
        {
            'oauth_id': 'fb-id-1',
            'email': 'fb@test.com',
            'name': 'FB User',
            'email_verified': True,
        },
    )
    response = facebook_oauth_client.get('/api/auth/facebook/callback?code=fake')
    assert response.status_code == 302
    assert 'auth=success' in response.location
    created = User.query.filter_by(
        oauth_provider='facebook', oauth_id='fb-id-1'
    ).first()
    assert created is not None
    assert created.id != existing_id
    assert User.query.filter_by(email='fb@test.com').count() == 2


def test_google_fetch_userinfo_requires_email_verified_true():
    from backend.api.oauth import _fetch_userinfo

    class FakeResp:
        def json(self):
            return {
                'sub': 'g1',
                'email': 'a@b.com',
                'name': 'A',
                'email_verified': True,
            }

    class FakeClient:
        def get(self, path, token=None):
            return FakeResp()

    profile = _fetch_userinfo(FakeClient(), 'google', {})
    assert profile['email_verified'] is True

    class UnverifiedResp:
        def json(self):
            return {
                'sub': 'g2',
                'email': 'b@b.com',
                'name': 'B',
                'email_verified': False,
            }

    class UnverifiedClient:
        def get(self, path, token=None):
            return UnverifiedResp()

    unverified = _fetch_userinfo(UnverifiedClient(), 'google', {})
    assert unverified['email_verified'] is False


def test_facebook_fetch_userinfo_never_reports_verified():
    from backend.api.oauth import _fetch_userinfo

    class FakeResp:
        def json(self):
            return {
                'id': 'f1',
                'email': 'a@b.com',
                'name': 'A',
                'verified': True,
                'email_verified': True,
            }

    class FakeClient:
        def get(self, path, token=None):
            return FakeResp()

    profile = _fetch_userinfo(FakeClient(), 'facebook', {})
    assert profile['email_verified'] is False
