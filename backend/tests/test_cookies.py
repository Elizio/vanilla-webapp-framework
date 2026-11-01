"""Cookie Path scoping for auth_token, csrf_token, and the Flask session."""

from http.cookies import SimpleCookie

import pytest

from backend import create_app
from backend.config.app_config import reset_app_config_for_tests
from backend.db_repository.database import db
from backend.tests.conftest import csrf_headers, login_user, register_user


def _parse_set_cookie_headers(headers):
    """Parse ``Set-Cookie`` headers into ``(name, morsel)`` pairs.

    Args:
        headers: Iterable of ``Set-Cookie`` header strings.

    Returns:
        List of ``(cookie_name, SimpleCookie morsel)`` tuples.
    """
    parsed = []
    for header in headers:
        cookie = SimpleCookie()
        cookie.load(header)
        for name, morsel in cookie.items():
            parsed.append((name, morsel))
    return parsed


def _cookies_named(headers, name):
    """Return morsels for ``name`` from ``Set-Cookie`` headers."""
    return [
        morsel
        for cookie_name, morsel in _parse_set_cookie_headers(headers)
        if cookie_name == name
    ]


def _stable_cookie_attrs(header):
    """Return Set-Cookie attributes excluding the value and Expires.

    Args:
        header: A single ``Set-Cookie`` header string.

    Returns:
        Semicolon-joined attribute string (Max-Age, flags, Path, SameSite).
    """
    parts = [part.strip() for part in header.split(';')[1:]]
    kept = [part for part in parts if not part.lower().startswith('expires=')]
    return '; '.join(kept)


def _scoped_csrf_headers(client):
    """Prime CSRF using an explicit Cookie header.

    The Flask test client will not send a cookie whose Path is
    ``/vanilla-webapp-framework`` to ``/api/*`` (Caddy strips that prefix
    in production, so the browser request path still matches). Tests that
    exercise a scoped Path must attach the cookie themselves.

    Args:
        client: Flask test client.

    Returns:
        Headers with ``X-CSRF-Token`` and ``Cookie``.
    """
    response = client.get('/api/csrf')
    token = response.json['csrf_token']
    return {
        'X-CSRF-Token': token,
        'Cookie': f'csrf_token={token}',
    }


def _make_app(monkeypatch, **env):
    """Create a test app after applying env overrides and resetting config."""
    for key, value in env.items():
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)
    monkeypatch.setenv('APP_PROFILE', env.get('APP_PROFILE', 'testing'))
    reset_app_config_for_tests()
    app = create_app()
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
    return app


@pytest.fixture
def default_client(monkeypatch):
    """Client with APP_BASE_PATH unset (local-dev default)."""
    monkeypatch.delenv('APP_BASE_PATH', raising=False)
    app = _make_app(monkeypatch)
    with app.app_context():
        db._Session.remove()
        db.Base.metadata.drop_all(db.engine)
        db.init_db()
    client = app.test_client()
    yield client
    monkeypatch.delenv('APP_BASE_PATH', raising=False)
    reset_app_config_for_tests()


@pytest.fixture
def scoped_app(monkeypatch):
    """App with cookies scoped to the production subpath."""
    app = _make_app(monkeypatch, APP_BASE_PATH='/vanilla-webapp-framework')
    with app.app_context():
        db._Session.remove()
        db.Base.metadata.drop_all(db.engine)
        db.init_db()
    yield app
    monkeypatch.delenv('APP_BASE_PATH', raising=False)
    reset_app_config_for_tests()


@pytest.fixture
def scoped_client(scoped_app):
    """Client that does not jar-filter cookies by Path.

    Production browsers send ``Path=/vanilla-webapp-framework`` cookies to
    ``/vanilla-webapp-framework/api/*`` before Caddy strips the prefix.
    The test client talks to ``/api/*`` directly, so cookie-jar Path
    matching would drop them; disable the jar and send Cookie headers.
    """
    return scoped_app.test_client(use_cookies=False)


def test_default_set_cookie_attrs_match_today(default_client):
    """With APP_BASE_PATH unset, cookie attributes stay Path=/ (local dev)."""
    csrf = default_client.get('/api/csrf')
    csrf_headers_list = csrf.headers.getlist('Set-Cookie')
    csrf_named = _cookies_named(csrf_headers_list, 'csrf_token')
    assert len(csrf_named) == 1
    assert csrf_named[0]['path'] == '/'
    assert csrf_named[0]['samesite'] == 'Lax'
    assert csrf_named[0]['httponly'] is True
    assert _stable_cookie_attrs(csrf_headers_list[0]) == (
        'HttpOnly; Path=/; SameSite=Lax'
    )

    register_user(default_client, username='cookieuser', password='testpass8')
    login = login_user(default_client, username='cookieuser', password='testpass8')
    auth_headers = [
        header
        for header in login.headers.getlist('Set-Cookie')
        if header.startswith('auth_token=')
    ]
    assert len(auth_headers) == 1
    assert _stable_cookie_attrs(auth_headers[0]) == (
        'Max-Age=3600; HttpOnly; Path=/; SameSite=Lax'
    )

    logout = default_client.post(
        '/api/logout',
        headers=csrf_headers(default_client),
    )
    logout_auth = _cookies_named(logout.headers.getlist('Set-Cookie'), 'auth_token')
    assert len(logout_auth) == 1
    assert logout_auth[0]['path'] == '/'
    assert logout_auth[0].value == ''
    assert _stable_cookie_attrs(logout.headers.getlist('Set-Cookie')[0]) == (
        'HttpOnly; Path=/; SameSite=Lax'
    )


def test_scoped_cookies_use_app_base_path(scoped_app, scoped_client):
    """Scoped deploy sets Path=/vanilla-webapp-framework on every cookie."""
    csrf = scoped_client.get('/api/csrf')
    scoped_csrf = [
        morsel
        for morsel in _cookies_named(csrf.headers.getlist('Set-Cookie'), 'csrf_token')
        if morsel['path'] == '/vanilla-webapp-framework'
    ]
    assert len(scoped_csrf) == 1
    assert scoped_csrf[0]['httponly'] is True

    register = scoped_client.post(
        '/api/register',
        json={'username': 'scopeduser', 'password': 'testpass8'},
        headers=_scoped_csrf_headers(scoped_client),
    )
    assert register.status_code == 201
    login = scoped_client.post(
        '/api/login',
        json={'username': 'scopeduser', 'password': 'testpass8'},
        headers=_scoped_csrf_headers(scoped_client),
    )
    assert login.status_code == 200
    scoped_auth = [
        morsel
        for morsel in _cookies_named(login.headers.getlist('Set-Cookie'), 'auth_token')
        if morsel['path'] == '/vanilla-webapp-framework' and morsel.value
    ]
    assert len(scoped_auth) == 1
    assert scoped_auth[0]['httponly'] is True
    assert scoped_auth[0]['samesite'] == 'Lax'

    assert scoped_app.config['SESSION_COOKIE_PATH'] == ('/vanilla-webapp-framework')
    session_client = scoped_app.test_client()
    with session_client.session_transaction() as session:
        session['oauth_state'] = 'probe'
    session_cookie = session_client.get_cookie(
        'session', path='/vanilla-webapp-framework'
    )
    assert session_cookie is not None
    assert session_cookie.path == '/vanilla-webapp-framework'


def test_scoped_logout_clears_cookie_at_app_base_path(scoped_client):
    """Logout expires the scoped auth_token, not only Path=/."""
    scoped_client.post(
        '/api/register',
        json={'username': 'logoutuser', 'password': 'testpass8'},
        headers=_scoped_csrf_headers(scoped_client),
    )
    scoped_client.post(
        '/api/login',
        json={'username': 'logoutuser', 'password': 'testpass8'},
        headers=_scoped_csrf_headers(scoped_client),
    )
    response = scoped_client.post(
        '/api/logout',
        headers=_scoped_csrf_headers(scoped_client),
    )
    scoped = [
        morsel
        for morsel in _cookies_named(
            response.headers.getlist('Set-Cookie'), 'auth_token'
        )
        if morsel['path'] == '/vanilla-webapp-framework'
    ]
    assert len(scoped) == 1
    assert scoped[0].value == ''
    assert scoped[0]['expires'] != ''


def test_legacy_root_cookies_are_expired_on_login_and_logout(scoped_client):
    """Issuing or clearing cookies also expires leftover Path=/ copies."""
    scoped_client.post(
        '/api/register',
        json={'username': 'legacyuser', 'password': 'testpass8'},
        headers=_scoped_csrf_headers(scoped_client),
    )
    login = scoped_client.post(
        '/api/login',
        json={'username': 'legacyuser', 'password': 'testpass8'},
        headers=_scoped_csrf_headers(scoped_client),
    )
    assert login.status_code == 200
    login_headers = login.headers.getlist('Set-Cookie')

    root_auth = [
        morsel
        for morsel in _cookies_named(login_headers, 'auth_token')
        if morsel['path'] == '/'
    ]
    assert len(root_auth) == 1
    assert root_auth[0].value == ''

    root_csrf = [
        morsel
        for morsel in _cookies_named(login_headers, 'csrf_token')
        if morsel['path'] == '/'
    ]
    assert len(root_csrf) == 1
    assert root_csrf[0].value == ''

    csrf = scoped_client.get('/api/csrf')
    root_csrf_on_issue = [
        morsel
        for morsel in _cookies_named(csrf.headers.getlist('Set-Cookie'), 'csrf_token')
        if morsel['path'] == '/'
    ]
    assert len(root_csrf_on_issue) == 1
    assert root_csrf_on_issue[0].value == ''

    logout = scoped_client.post(
        '/api/logout',
        headers=_scoped_csrf_headers(scoped_client),
    )
    logout_headers = logout.headers.getlist('Set-Cookie')
    root_auth_logout = [
        morsel
        for morsel in _cookies_named(logout_headers, 'auth_token')
        if morsel['path'] == '/'
    ]
    root_csrf_logout = [
        morsel
        for morsel in _cookies_named(logout_headers, 'csrf_token')
        if morsel['path'] == '/'
    ]
    assert len(root_auth_logout) == 1
    assert root_auth_logout[0].value == ''
    assert len(root_csrf_logout) == 1
    assert root_csrf_logout[0].value == ''


def test_default_does_not_emit_duplicate_root_expiry(default_client):
    """Local dev (Path=/) must not send a second expiry Set-Cookie."""
    csrf = default_client.get('/api/csrf')
    assert len(_cookies_named(csrf.headers.getlist('Set-Cookie'), 'csrf_token')) == 1

    register_user(default_client, username='nodup', password='testpass8')
    login = login_user(default_client, username='nodup', password='testpass8')
    assert len(_cookies_named(login.headers.getlist('Set-Cookie'), 'auth_token')) == 1
