"""Cookie Path scoping for auth_token, csrf_token, and the Flask session."""

from http.cookies import SimpleCookie

import pytest

from backend import create_app
from backend.config.app_config import reset_app_config_for_tests
from backend.db_repository.database import db
from backend.config.cookie_names import (
    LEGACY_AUTH_COOKIE_NAME,
    LEGACY_CSRF_COOKIE_NAME,
    LEGACY_DEVICE_COOKIE_NAME,
    LEGACY_REFRESH_COOKIE_NAME,
)
from backend.tests.conftest import (
    csrf_headers,
    live_cookie_name,
    login_user,
    refresh_session,
    register_user,
)


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
    name = live_cookie_name(client, 'CSRF_COOKIE_NAME')
    return {
        'X-CSRF-Token': token,
        'Cookie': f'{name}={token}',
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
    csrf_name = live_cookie_name(default_client, 'CSRF_COOKIE_NAME')
    auth_name = live_cookie_name(default_client, 'AUTH_COOKIE_NAME')
    refresh_name = live_cookie_name(default_client, 'REFRESH_COOKIE_NAME')
    device_name = live_cookie_name(default_client, 'AUTH_DEVICE_COOKIE_NAME')

    csrf = default_client.get('/api/csrf')
    csrf_headers_list = csrf.headers.getlist('Set-Cookie')
    csrf_named = [
        morsel
        for morsel in _cookies_named(csrf_headers_list, csrf_name)
        if morsel.value
    ]
    assert len(csrf_named) == 1
    assert csrf_named[0]['path'] == '/'
    assert csrf_named[0]['samesite'] == 'Lax'
    assert csrf_named[0]['httponly'] is True
    live_csrf_header = [
        header
        for header in csrf_headers_list
        if header.startswith(f'{csrf_name}=') and 'expires=' not in header.lower()
    ]
    assert live_csrf_header
    assert _stable_cookie_attrs(live_csrf_header[0]) == (
        'HttpOnly; Path=/; SameSite=Lax'
    )

    register_user(default_client, username='cookieuser', password='testpass8')
    login = login_user(default_client, username='cookieuser', password='testpass8')
    auth_headers = [
        header
        for header in login.headers.getlist('Set-Cookie')
        if header.startswith(f'{auth_name}=') and 'Max-Age=' in header
    ]
    assert len(auth_headers) == 1
    assert _stable_cookie_attrs(auth_headers[0]) == (
        'Max-Age=900; HttpOnly; Path=/; SameSite=Lax'
    )
    refresh_headers = [
        header
        for header in login.headers.getlist('Set-Cookie')
        if header.startswith(f'{refresh_name}=')
        and 'Path=/api/auth' in header
        and not header.startswith(f'{refresh_name}=;')
        and 'expires=' not in header.lower()
    ]
    assert len(refresh_headers) == 1
    attrs = _stable_cookie_attrs(refresh_headers[0])
    assert 'HttpOnly' in attrs
    assert 'Path=/api/auth' in attrs
    assert 'SameSite=Strict' in attrs
    assert 'Max-Age=' not in attrs
    device_headers = [
        header
        for header in login.headers.getlist('Set-Cookie')
        if header.startswith(f'{device_name}=') and 'Max-Age=' in header
    ]
    assert len(device_headers) == 1
    assert _stable_cookie_attrs(device_headers[0]) == (
        'Max-Age=2592000; HttpOnly; Path=/; SameSite=Lax'
    )

    logout = default_client.post(
        '/api/auth/logout',
        headers=csrf_headers(default_client),
    )
    logout_auth = [
        morsel
        for morsel in _cookies_named(logout.headers.getlist('Set-Cookie'), auth_name)
        if morsel['path'] == '/'
    ]
    assert len(logout_auth) == 1
    assert logout_auth[0].value == ''
    logout_refresh = [
        morsel
        for morsel in _cookies_named(logout.headers.getlist('Set-Cookie'), refresh_name)
        if morsel['path'] == '/api/auth'
    ]
    assert len(logout_refresh) == 1
    assert logout_refresh[0].value == ''


def test_scoped_cookies_use_app_base_path(scoped_app, scoped_client):
    """Scoped deploy sets Path=/vanilla-webapp-framework on every cookie."""
    csrf_name = live_cookie_name(scoped_client, 'CSRF_COOKIE_NAME')
    auth_name = live_cookie_name(scoped_client, 'AUTH_COOKIE_NAME')
    refresh_name = live_cookie_name(scoped_client, 'REFRESH_COOKIE_NAME')
    device_name = live_cookie_name(scoped_client, 'AUTH_DEVICE_COOKIE_NAME')
    csrf = scoped_client.get('/api/csrf')
    scoped_csrf = [
        morsel
        for morsel in _cookies_named(csrf.headers.getlist('Set-Cookie'), csrf_name)
        if morsel['path'] == '/vanilla-webapp-framework' and morsel.value
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
        for morsel in _cookies_named(login.headers.getlist('Set-Cookie'), auth_name)
        if morsel['path'] == '/vanilla-webapp-framework' and morsel.value
    ]
    assert len(scoped_auth) == 1
    assert scoped_auth[0]['httponly'] is True
    assert scoped_auth[0]['samesite'] == 'Lax'
    scoped_device = [
        morsel
        for morsel in _cookies_named(login.headers.getlist('Set-Cookie'), device_name)
        if morsel['path'] == '/vanilla-webapp-framework' and morsel.value
    ]
    assert len(scoped_device) == 1
    assert scoped_device[0]['httponly'] is True
    assert scoped_device[0]['samesite'] == 'Lax'
    login_cookies = login.headers.getlist('Set-Cookie')
    scoped_refresh = [
        morsel
        for morsel in _cookies_named(login_cookies, refresh_name)
        if morsel['path'] == '/vanilla-webapp-framework/api/auth' and morsel.value
    ]
    assert len(scoped_refresh) == 1
    assert scoped_refresh[0]['httponly'] is True
    assert scoped_refresh[0]['samesite'] == 'Strict'

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
    """Logout expires the scoped auth cookie, not only Path=/."""
    auth_name = live_cookie_name(scoped_client, 'AUTH_COOKIE_NAME')
    refresh_name = live_cookie_name(scoped_client, 'REFRESH_COOKIE_NAME')
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
        '/api/auth/logout',
        headers=_scoped_csrf_headers(scoped_client),
    )
    scoped = [
        morsel
        for morsel in _cookies_named(response.headers.getlist('Set-Cookie'), auth_name)
        if morsel['path'] == '/vanilla-webapp-framework'
    ]
    assert len(scoped) == 1
    assert scoped[0].value == ''
    assert scoped[0]['expires'] != ''
    scoped_refresh = [
        morsel
        for morsel in _cookies_named(
            response.headers.getlist('Set-Cookie'), refresh_name
        )
        if morsel['path'] == '/vanilla-webapp-framework/api/auth'
    ]
    assert len(scoped_refresh) == 1
    assert scoped_refresh[0].value == ''


def test_legacy_root_cookies_are_expired_on_login_and_logout(scoped_client):
    """Issuing or clearing cookies also expires leftover Path=/ copies."""
    live_auth = live_cookie_name(scoped_client, 'AUTH_COOKIE_NAME')
    live_csrf = live_cookie_name(scoped_client, 'CSRF_COOKIE_NAME')
    live_refresh = live_cookie_name(scoped_client, 'REFRESH_COOKIE_NAME')
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
        '/api/auth/logout',
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
    leftover_refresh = [
        morsel
        for morsel in _cookies_named(logout_headers, live_refresh)
        if morsel['path'] in ('/', '/api/auth')
    ]
    leftover_legacy_refresh = [
        morsel
        for morsel in _cookies_named(logout_headers, LEGACY_REFRESH_COOKIE_NAME)
        if morsel['path'] in ('/', '/api/auth')
    ]
    assert leftover_refresh
    assert leftover_legacy_refresh
    assert all(morsel.value == '' for morsel in leftover_refresh)
    assert all(morsel.value == '' for morsel in leftover_legacy_refresh)
    live_root_auth = [
        morsel
        for morsel in _cookies_named(login_headers, live_auth)
        if morsel['path'] == '/'
    ]
    assert len(live_root_auth) == 1
    assert live_root_auth[0].value == ''
    live_root_csrf = [
        morsel
        for morsel in _cookies_named(
            scoped_client.get('/api/csrf').headers.getlist('Set-Cookie'), live_csrf
        )
        if morsel['path'] == '/'
    ]
    assert len(live_root_csrf) == 1
    assert live_root_csrf[0].value == ''


def test_default_does_not_emit_duplicate_root_expiry(default_client):
    """Local dev (Path=/) must not send a second expiry of the live cookie."""
    csrf_name = live_cookie_name(default_client, 'CSRF_COOKIE_NAME')
    auth_name = live_cookie_name(default_client, 'AUTH_COOKIE_NAME')
    refresh_name = live_cookie_name(default_client, 'REFRESH_COOKIE_NAME')
    csrf = default_client.get('/api/csrf')
    live_csrf = [
        morsel
        for morsel in _cookies_named(csrf.headers.getlist('Set-Cookie'), csrf_name)
        if morsel.value
    ]
    assert len(live_csrf) == 1

    register_user(default_client, username='nodup', password='testpass8')
    login = login_user(default_client, username='nodup', password='testpass8')
    live_auth = [
        morsel
        for morsel in _cookies_named(login.headers.getlist('Set-Cookie'), auth_name)
        if morsel.value
    ]
    assert len(live_auth) == 1
    assert (
        len(
            [
                morsel
                for morsel in _cookies_named(
                    login.headers.getlist('Set-Cookie'), refresh_name
                )
                if morsel.value
            ]
        )
        == 1
    )


def test_remember_me_sets_persistent_refresh_cookie(default_client):
    """Remember-me login sets Max-Age on the refresh cookie (~30 days)."""
    register_user(default_client, username='remember', password='testpass8')
    login = login_user(
        default_client, username='remember', password='testpass8', remember_me=True
    )
    assert login.status_code == 200
    refresh = [
        morsel
        for morsel in _cookies_named(
            login.headers.getlist('Set-Cookie'),
            live_cookie_name(default_client, 'REFRESH_COOKIE_NAME'),
        )
        if morsel.value and morsel['path'] == '/api/auth'
    ]
    assert len(refresh) == 1
    max_age = int(refresh[0]['max-age'])
    assert 30 * 24 * 3600 - 5 <= max_age <= 30 * 24 * 3600


def test_production_refresh_cookie_is_secure(monkeypatch):
    """Refresh cookie sets Secure in the production profile."""
    app = _make_app(monkeypatch, APP_PROFILE='production')
    with app.app_context():
        db._Session.remove()
        db.Base.metadata.drop_all(db.engine)
        db.init_db()
    client = app.test_client()
    try:
        register_user(client, username='secureuser', password='testpass8')
        login = login_user(client, username='secureuser', password='testpass8')
        refresh = [
            morsel
            for morsel in _cookies_named(
                login.headers.getlist('Set-Cookie'),
                live_cookie_name(client, 'REFRESH_COOKIE_NAME'),
            )
            if morsel.value and morsel['path'] == '/api/auth'
        ]
        assert len(refresh) == 1
        assert refresh[0]['secure'] is True
        auth = [
            morsel
            for morsel in _cookies_named(
                login.headers.getlist('Set-Cookie'),
                live_cookie_name(client, 'AUTH_COOKIE_NAME'),
            )
            if morsel.value
        ]
        assert auth[0]['secure'] is True
    finally:
        monkeypatch.delenv('APP_PROFILE', raising=False)
        reset_app_config_for_tests()


def _csrf_post_headers(client, cookie_header):
    """Prime CSRF and return headers using an explicit Cookie string."""
    response = client.get('/api/csrf')
    token = response.json['csrf_token']
    return {
        'X-CSRF-Token': token,
        'Cookie': cookie_header.format(
            token=token,
            live=live_cookie_name(client, 'CSRF_COOKIE_NAME'),
            legacy=LEGACY_CSRF_COOKIE_NAME,
        ),
        'token': token,
    }


def test_csrf_accepts_matching_value_when_foreign_cookie_is_first(default_client):
    """Safari-style ``csrf_token=bogus; csrf_token=good`` must not 403."""
    app = default_client.application
    client = app.test_client(use_cookies=False)
    primed = _csrf_post_headers(client, '{live}=bogus; {live}={token}')
    token = primed.pop('token')
    response = client.post(
        '/api/register',
        json={'username': 'dupcsrf', 'password': 'testpass8'},
        headers=primed,
    )
    assert token
    assert response.status_code == 201


def test_csrf_accepts_legacy_name_when_foreign_value_is_first(default_client):
    """A leftover Path=/ ``csrf_token`` sent first still matches the header."""
    app = default_client.application
    client = app.test_client(use_cookies=False)
    primed = _csrf_post_headers(client, '{legacy}=bogus; {live}={token}')
    primed.pop('token')
    response = client.post(
        '/api/register',
        json={'username': 'legacyfirst', 'password': 'testpass8'},
        headers=primed,
    )
    assert response.status_code == 201


def test_csrf_accepts_legacy_cookie_name_alone(default_client):
    """Pre-upgrade sessions that only send ``csrf_token`` still work."""
    app = default_client.application
    client = app.test_client(use_cookies=False)
    primed = _csrf_post_headers(client, '{legacy}={token}')
    primed.pop('token')
    response = client.post(
        '/api/register',
        json={'username': 'legacyonly', 'password': 'testpass8'},
        headers=primed,
    )
    assert response.status_code == 201


def test_csrf_rejects_when_no_cookie_matches_header(default_client):
    """A header that matches none of the cookie values is still 403."""
    app = default_client.application
    client = app.test_client(use_cookies=False)
    primed = _csrf_post_headers(client, '{live}=bogus; {legacy}=also-bogus')
    primed.pop('token')
    response = client.post(
        '/api/register',
        json={'username': 'nomatch', 'password': 'testpass8'},
        headers=primed,
    )
    assert response.status_code == 403
    assert response.json['code'] == 'CSRF_INVALID'


def test_legacy_auth_cookie_still_authenticates(default_client):
    """A pre-upgrade ``auth_token`` cookie keeps the session logged in."""
    register_user(default_client, username='legacyauth', password='testpass8')
    login_user(default_client, username='legacyauth', password='testpass8')
    auth_name = live_cookie_name(default_client, 'AUTH_COOKIE_NAME')
    cookie = default_client.get_cookie(auth_name)
    assert cookie is not None
    token = cookie.value
    default_client.delete_cookie(auth_name)
    default_client.set_cookie(LEGACY_AUTH_COOKIE_NAME, token)
    assert default_client.get('/api/data').status_code == 200


def test_issuing_cookies_expires_legacy_names_at_app_path(default_client):
    """New cookies expire the old names at the live path (and Path=/)."""
    csrf = default_client.get('/api/csrf')
    legacy_csrf = [
        morsel
        for morsel in _cookies_named(
            csrf.headers.getlist('Set-Cookie'), LEGACY_CSRF_COOKIE_NAME
        )
        if morsel['path'] == '/'
    ]
    assert len(legacy_csrf) == 1
    assert legacy_csrf[0].value == ''

    register_user(default_client, username='expirelegacy', password='testpass8')
    login = login_user(default_client, username='expirelegacy', password='testpass8')
    login_headers = login.headers.getlist('Set-Cookie')
    for name in (
        LEGACY_AUTH_COOKIE_NAME,
        LEGACY_CSRF_COOKIE_NAME,
        LEGACY_DEVICE_COOKIE_NAME,
    ):
        expired = [
            morsel
            for morsel in _cookies_named(login_headers, name)
            if morsel['path'] == '/'
        ]
        assert expired
        assert all(morsel.value == '' for morsel in expired)
    expired_refresh = [
        morsel
        for morsel in _cookies_named(login_headers, LEGACY_REFRESH_COOKIE_NAME)
        if morsel['path'] == '/api/auth'
    ]
    assert expired_refresh
    assert all(morsel.value == '' for morsel in expired_refresh)


def test_two_apps_on_one_domain_do_not_collide(monkeypatch):
    """Distinct APP_NAME values issue distinct cookie names on one host."""
    app_a = _make_app(monkeypatch, APP_NAME='vanilla-webapp-framework')
    with app_a.app_context():
        db._Session.remove()
        db.Base.metadata.drop_all(db.engine)
        db.init_db()
    app_b = _make_app(monkeypatch, APP_NAME='garage-boss')
    with app_b.app_context():
        db._Session.remove()
        db.Base.metadata.drop_all(db.engine)
        db.init_db()
    try:
        names_a = {
            app_a.config['CSRF_COOKIE_NAME'],
            app_a.config['AUTH_COOKIE_NAME'],
            app_a.config['REFRESH_COOKIE_NAME'],
            app_a.config['AUTH_DEVICE_COOKIE_NAME'],
        }
        names_b = {
            app_b.config['CSRF_COOKIE_NAME'],
            app_b.config['AUTH_COOKIE_NAME'],
            app_b.config['REFRESH_COOKIE_NAME'],
            app_b.config['AUTH_DEVICE_COOKIE_NAME'],
        }
        assert names_a.isdisjoint(names_b)
        assert app_a.config['CSRF_COOKIE_NAME'] == (
            'vanilla-webapp-framework_csrf_token'
        )
        assert app_b.config['CSRF_COOKIE_NAME'] == 'garage-boss_csrf_token'

        client_a = app_a.test_client(use_cookies=False)
        client_b = app_b.test_client(use_cookies=False)
        csrf_a = client_a.get('/api/csrf')
        csrf_b = client_b.get('/api/csrf')
        token_a = csrf_a.json['csrf_token']
        token_b = csrf_b.json['csrf_token']
        name_a = app_a.config['CSRF_COOKIE_NAME']
        name_b = app_b.config['CSRF_COOKIE_NAME']
        collided = client_a.post(
            '/api/register',
            json={'username': 'appa', 'password': 'testpass8'},
            headers={
                'X-CSRF-Token': token_a,
                'Cookie': f'{name_b}={token_b}; {name_a}={token_a}',
            },
        )
        assert collided.status_code == 201
        foreign_only = client_a.post(
            '/api/login',
            json={'username': 'appa', 'password': 'testpass8'},
            headers={
                'X-CSRF-Token': token_a,
                'Cookie': f'{name_b}={token_b}',
            },
        )
        assert foreign_only.status_code == 403
        assert foreign_only.json['code'] == 'CSRF_INVALID'
    finally:
        monkeypatch.delenv('APP_NAME', raising=False)
        reset_app_config_for_tests()


def test_subpath_app_base_path_csrf_still_works(scoped_client):
    """Mutating requests under APP_BASE_PATH succeed with the scoped cookie."""
    response = scoped_client.post(
        '/api/register',
        json={'username': 'subpathcsrf', 'password': 'testpass8'},
        headers=_scoped_csrf_headers(scoped_client),
    )
    assert response.status_code == 201
    login = scoped_client.post(
        '/api/login',
        json={'username': 'subpathcsrf', 'password': 'testpass8'},
        headers=_scoped_csrf_headers(scoped_client),
    )
    assert login.status_code == 200
    auth_name = live_cookie_name(scoped_client, 'AUTH_COOKIE_NAME')
    scoped_auth = [
        morsel
        for morsel in _cookies_named(login.headers.getlist('Set-Cookie'), auth_name)
        if morsel['path'] == '/vanilla-webapp-framework' and morsel.value
    ]
    assert len(scoped_auth) == 1


def test_csrf_non_ascii_cookie_or_header_returns_403_not_500(default_client):
    """Planted non-ASCII CSRF cookie or header must 403, not TypeError 500."""
    app = default_client.application
    client = app.test_client(use_cookies=False)
    live = live_cookie_name(client, 'CSRF_COOKIE_NAME')
    planted_cookie = client.post(
        '/api/login',
        json={'username': 'x', 'password': 'y'},
        headers={
            'X-CSRF-Token': 'ascii-token',
            'Cookie': f'{live}=cafés',
        },
    )
    assert planted_cookie.status_code == 403
    assert planted_cookie.json['code'] == 'CSRF_INVALID'
    planted_header = client.post(
        '/api/login',
        json={'username': 'x', 'password': 'y'},
        headers={
            'X-CSRF-Token': 'cafés',
            'Cookie': f'{live}=ascii-token',
        },
    )
    assert planted_header.status_code == 403
    assert planted_header.json['code'] == 'CSRF_INVALID'


def test_csrf_rejects_empty_header_and_empty_cookie(default_client):
    """Empty X-CSRF-Token with an empty cookie is 403, not a match."""
    app = default_client.application
    client = app.test_client(use_cookies=False)
    live = live_cookie_name(client, 'CSRF_COOKIE_NAME')
    response = client.post(
        '/api/login',
        json={'username': 'x', 'password': 'y'},
        headers={
            'X-CSRF-Token': '',
            'Cookie': f'{live}=',
        },
    )
    assert response.status_code == 403
    assert response.json['code'] == 'CSRF_INVALID'


def test_legacy_refresh_cookie_rotates_to_namespaced_name(default_client):
    """Refresh with only ``refresh_token`` issues the namespaced cookie."""
    register_user(default_client, username='legacyref', password='testpass8')
    login_user(default_client, username='legacyref', password='testpass8')
    live = live_cookie_name(default_client, 'REFRESH_COOKIE_NAME')
    cookie = default_client.get_cookie(live, path='/api/auth')
    assert cookie is not None
    token = cookie.value
    default_client.delete_cookie(live, path='/api/auth')
    default_client.set_cookie(LEGACY_REFRESH_COOKIE_NAME, token, path='/api/auth')
    response = refresh_session(default_client)
    assert response.status_code == 200
    headers = response.headers.getlist('Set-Cookie')
    live_set = [
        morsel
        for morsel in _cookies_named(headers, live)
        if morsel.value and morsel['path'] == '/api/auth'
    ]
    assert len(live_set) == 1
    legacy_expired = [
        morsel
        for morsel in _cookies_named(headers, LEGACY_REFRESH_COOKIE_NAME)
        if morsel['path'] == '/api/auth'
    ]
    assert legacy_expired
    assert all(morsel.value == '' for morsel in legacy_expired)


def test_logout_clears_legacy_and_namespaced_cookie_names(default_client):
    """Logout expires both the live names and the unprefixed leftovers."""
    register_user(default_client, username='clearboth', password='testpass8')
    login_user(default_client, username='clearboth', password='testpass8')
    logout = default_client.post(
        '/api/auth/logout',
        headers=csrf_headers(default_client),
    )
    assert logout.status_code == 200
    headers = logout.headers.getlist('Set-Cookie')
    names = (
        live_cookie_name(default_client, 'AUTH_COOKIE_NAME'),
        live_cookie_name(default_client, 'REFRESH_COOKIE_NAME'),
        LEGACY_AUTH_COOKIE_NAME,
        LEGACY_REFRESH_COOKIE_NAME,
    )
    for name in names:
        expired = _cookies_named(headers, name)
        assert expired, name
        assert all(morsel.value == '' for morsel in expired), name
