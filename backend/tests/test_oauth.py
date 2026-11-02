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


@pytest.mark.parametrize('provider', ['google', 'facebook'])
def test_unconfigured_login_returns_provider_not_configured(
    test_app, test_client, test_db, provider
):
    """Login stays 404 PROVIDER_NOT_CONFIGURED when credentials are unset."""
    _clear_oauth_config(test_app)
    response = test_client.get(f'/api/auth/{provider}/login')
    assert response.status_code == 404
    assert response.json == {'code': 'PROVIDER_NOT_CONFIGURED'}


@pytest.mark.parametrize('provider', ['google', 'facebook'])
def test_unconfigured_callback_returns_provider_not_configured(
    test_app, test_client, test_db, provider
):
    """Callback stays 404 PROVIDER_NOT_CONFIGURED when credentials are unset."""
    _clear_oauth_config(test_app)
    response = test_client.get(f'/api/auth/{provider}/callback?code=fake')
    assert response.status_code == 404
    assert response.json == {'code': 'PROVIDER_NOT_CONFIGURED'}


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


def test_facebook_never_links_by_email(facebook_oauth_client, test_db, monkeypatch):
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


@pytest.fixture
def both_oauth_client(test_app, test_db):
    """Test client with Google and Facebook OAuth configured."""
    test_app.config['GOOGLE_CLIENT_ID'] = 'test-google-id'
    test_app.config['GOOGLE_CLIENT_SECRET'] = 'test-google-secret'
    test_app.config['FACEBOOK_CLIENT_ID'] = 'test-facebook-id'
    test_app.config['FACEBOOK_CLIENT_SECRET'] = 'test-facebook-secret'
    test_app.config['OAUTH_REDIRECT_BASE'] = 'http://localhost'
    test_app.config['FRONTEND_URL'] = 'http://localhost'
    register_oauth_clients(test_app)
    return test_app.test_client()


def test_list_providers_google_and_facebook(both_oauth_client):
    response = both_oauth_client.get('/api/auth/providers')
    assert response.status_code == 200
    assert response.json == ['facebook', 'google']


def test_facebook_callback_creates_user(facebook_oauth_client, monkeypatch):
    """Facebook callback creates an OAuth-only user for that provider."""
    _patch_oauth_callback(
        monkeypatch,
        {
            'oauth_id': 'fb-oauth-123',
            'email': 'fb-social@test.com',
            'name': 'FB Social',
            'email_verified': False,
        },
    )
    response = facebook_oauth_client.get('/api/auth/facebook/callback?code=fake')
    assert response.status_code == 302
    assert 'auth=success' in response.location
    assert AUTH_COOKIE_NAME in response.headers.getlist('Set-Cookie')[0]

    user = User.query.filter_by(
        oauth_provider='facebook', oauth_id='fb-oauth-123'
    ).first()
    assert user is not None
    assert user.email == 'fb-social@test.com'
    assert user.password_hash is None


def test_facebook_callback_username_from_name(facebook_oauth_client, monkeypatch):
    """When Facebook omits email, the username is derived from the display name."""
    _patch_oauth_callback(
        monkeypatch,
        {
            'oauth_id': 'fb-name-only',
            'email': None,
            'name': 'Ada Lovelace',
            'email_verified': False,
        },
    )
    facebook_oauth_client.get('/api/auth/facebook/callback?code=fake')
    user = User.query.filter_by(
        oauth_provider='facebook', oauth_id='fb-name-only'
    ).first()
    assert user is not None
    assert user.username == 'adalovelace'


def test_facebook_callback_username_from_provider_id(
    facebook_oauth_client, monkeypatch
):
    """When Facebook omits email and name, the username uses the provider id."""
    _patch_oauth_callback(
        monkeypatch,
        {
            'oauth_id': 'abcdefghijklmnop',
            'email': None,
            'name': None,
            'email_verified': False,
        },
    )
    facebook_oauth_client.get('/api/auth/facebook/callback?code=fake')
    user = User.query.filter_by(
        oauth_provider='facebook', oauth_id='abcdefghijklmnop'
    ).first()
    assert user is not None
    assert user.username == 'facebook_abcdefgh'


def test_oauth_username_collision_adds_suffix(
    facebook_oauth_client, test_db, monkeypatch
):
    """A taken username gets a numeric suffix."""
    existing = User(username='fbuser', password_hash='hashed')
    db_session.add(existing)
    db_session.commit()
    db_session.expunge_all()
    _patch_oauth_callback(
        monkeypatch,
        {
            'oauth_id': 'fb-collide',
            'email': 'fbuser@test.com',
            'name': 'X',
            'email_verified': False,
        },
    )
    facebook_oauth_client.get('/api/auth/facebook/callback?code=fake')
    user = User.query.filter_by(
        oauth_provider='facebook', oauth_id='fb-collide'
    ).first()
    assert user is not None
    assert user.username == 'fbuser1'


def test_fetch_userinfo_rejects_unknown_provider():
    from backend.api.oauth import _fetch_userinfo

    with pytest.raises(ValueError, match='Unsupported provider'):
        _fetch_userinfo(None, 'twitter', {})


def test_google_fetch_userinfo_from_token_payload():
    """Google OIDC tokens may already include userinfo."""
    from backend.api.oauth import _fetch_userinfo

    profile = _fetch_userinfo(
        None,
        'google',
        {
            'userinfo': {
                'sub': 'g-token',
                'email': 'g@test.com',
                'name': 'G',
                'email_verified': True,
            }
        },
    )
    assert profile['oauth_id'] == 'g-token'
    assert profile['email'] == 'g@test.com'
    assert profile['email_verified'] is True


def test_facebook_fetch_userinfo_maps_id_email_name():
    """Facebook Graph ``me`` maps id/email/name and pins the API version."""
    from backend.api.oauth import FACEBOOK_GRAPH_API_VERSION, _fetch_userinfo

    captured = {}

    class FakeResp:
        def json(self):
            return {
                'id': 'fb-42',
                'email': 'fb@test.com',
                'name': 'FB Name',
            }

    class FakeClient:
        def get(self, path, token=None):
            captured['path'] = path
            return FakeResp()

    profile = _fetch_userinfo(FakeClient(), 'facebook', {'access_token': 'fake'})
    assert profile == {
        'oauth_id': 'fb-42',
        'email': 'fb@test.com',
        'name': 'FB Name',
        'email_verified': False,
    }
    assert FACEBOOK_GRAPH_API_VERSION != 'v19.0'
    assert FACEBOOK_GRAPH_API_VERSION in captured['path']
    assert captured['path'].endswith('me?fields=id,name,email')


def test_login_redirect_uri_includes_subpath(oauth_client, test_app, monkeypatch):
    """OAUTH_REDIRECT_BASE keeps the production subpath on the callback URI."""
    from flask import redirect
    from backend.api import oauth as oauth_module

    test_app.config['OAUTH_REDIRECT_BASE'] = (
        'https://dsfor.fun/vanilla-webapp-framework'
    )
    captured = {}

    class FakeClient:
        def authorize_redirect(self, redirect_uri):
            captured['uri'] = redirect_uri
            return redirect('https://accounts.google.com/o/oauth2/v2/auth')

    monkeypatch.setattr(
        oauth_module.oauth,
        'create_client',
        lambda _provider: FakeClient(),
    )
    response = oauth_client.get('/api/auth/google/login')
    assert response.status_code == 302
    assert captured['uri'] == (
        'https://dsfor.fun/vanilla-webapp-framework/api/auth/google/callback'
    )


def test_callback_redirects_to_frontend_subpath(oauth_client, test_app, monkeypatch):
    """FRONTEND_URL with a subpath is where the cookie redirect lands."""
    test_app.config['FRONTEND_URL'] = 'https://dsfor.fun/vanilla-webapp-framework'
    _patch_oauth_callback(
        monkeypatch,
        {
            'oauth_id': 'oauth-subpath',
            'email': 'subpath@test.com',
            'name': 'Subpath',
            'email_verified': True,
        },
    )
    response = oauth_client.get('/api/auth/google/callback?code=fake')
    assert response.status_code == 302
    assert response.location.startswith(
        'https://dsfor.fun/vanilla-webapp-framework/?auth=success'
    )


def test_facebook_client_urls_use_supported_graph_api_version(
    facebook_oauth_client,
):
    """Authorize and token URLs share one non-retired Graph API version."""
    from backend.api.oauth import FACEBOOK_GRAPH_API_VERSION, oauth

    assert FACEBOOK_GRAPH_API_VERSION != 'v19.0'
    assert FACEBOOK_GRAPH_API_VERSION.startswith('v')
    _overwrite, kwargs = oauth._registry['facebook']
    assert FACEBOOK_GRAPH_API_VERSION in kwargs['authorize_url']
    assert FACEBOOK_GRAPH_API_VERSION in kwargs['access_token_url']
    assert 'v19.0' not in kwargs['authorize_url']
    assert 'v19.0' not in kwargs['access_token_url']


def test_production_warns_when_oauth_redirect_base_empty(test_app, test_db):
    """Production with providers enabled warns if OAUTH_REDIRECT_BASE is empty."""
    from unittest.mock import patch

    from backend.api.oauth import enabled_providers

    test_app.config['APP_PROFILE'] = 'production'
    test_app.config['OAUTH_REDIRECT_BASE'] = ''
    test_app.config['GOOGLE_CLIENT_ID'] = 'test-google-id'
    test_app.config['GOOGLE_CLIENT_SECRET'] = 'test-google-secret'
    test_app.config['FACEBOOK_CLIENT_ID'] = ''
    test_app.config['FACEBOOK_CLIENT_SECRET'] = ''

    with patch.object(test_app.logger, 'warning') as warn:
        register_oauth_clients(test_app)

    warn.assert_called()
    message = warn.call_args[0][0]
    if len(warn.call_args[0]) > 1:
        message = message % warn.call_args[0][1:]
    assert 'OAUTH_REDIRECT_BASE' in message
    assert 'test-google-id' not in message
    assert 'test-google-secret' not in message
    assert 'google' in enabled_providers()


def test_production_no_warning_when_redirect_base_set(test_app, test_db):
    """A public OAUTH_REDIRECT_BASE in production does not warn."""
    from unittest.mock import patch

    test_app.config['APP_PROFILE'] = 'production'
    test_app.config['OAUTH_REDIRECT_BASE'] = (
        'https://dsfor.fun/vanilla-webapp-framework'
    )
    test_app.config['GOOGLE_CLIENT_ID'] = 'test-google-id'
    test_app.config['GOOGLE_CLIENT_SECRET'] = 'test-google-secret'

    with patch.object(test_app.logger, 'warning') as warn:
        register_oauth_clients(test_app)

    for call in warn.call_args_list:
        message = call[0][0]
        if len(call[0]) > 1:
            message = message % call[0][1:]
        assert 'OAUTH_REDIRECT_BASE' not in message


def test_production_no_warning_when_providers_unconfigured(test_app, test_db):
    """Unconfigured production (today's live default) stays silent and safe."""
    from unittest.mock import patch

    test_app.config['APP_PROFILE'] = 'production'
    test_app.config['OAUTH_REDIRECT_BASE'] = ''
    _clear_oauth_config(test_app)

    with patch.object(test_app.logger, 'warning') as warn:
        register_oauth_clients(test_app)

    for call in warn.call_args_list:
        message = call[0][0]
        if len(call[0]) > 1:
            message = message % call[0][1:]
        assert 'OAUTH_REDIRECT_BASE' not in message
