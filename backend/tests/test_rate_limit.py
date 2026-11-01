"""Login/register rate-limit behaviour: IP, username, shared SQLite store."""

from __future__ import annotations

import threading
from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, event, text

from backend.tests.conftest import csrf_headers, login_user, register_user


def _enable_rate_limit(app, *, username_max: int | None = None) -> None:
    """Turn the limiter on for a Flask app created under the testing profile.

    Args:
        app: Flask app.
        username_max: Optional override so IP-only tests do not trip the
            per-username lockout first.
    """
    app.config['RATELIMIT_ENABLED'] = True
    if username_max is not None:
        app.config['RATELIMIT_LOGIN_USER_MAX'] = username_max


def _login(
    client,
    username: str,
    password: str,
    remote_addr: str = '127.0.0.1',
    extra_headers: dict | None = None,
):
    """POST /api/login with CSRF and an explicit REMOTE_ADDR."""
    headers = csrf_headers(client)
    if extra_headers:
        headers.update(extra_headers)
    return client.post(
        '/api/login',
        json={'username': username, 'password': password},
        headers=headers,
        environ_base={'REMOTE_ADDR': remote_addr},
    )


def _register(
    client,
    username: str,
    password: str = 'testpass8',
    remote_addr: str = '127.0.0.1',
):
    """POST /api/register with CSRF and an explicit REMOTE_ADDR."""
    return client.post(
        '/api/register',
        json={'username': username, 'password': password},
        headers=csrf_headers(client),
        environ_base={'REMOTE_ADDR': remote_addr},
    )


def _assert_rate_limited(response) -> None:
    """Assert the app JSON 429 shape plus Retry-After."""
    assert response.status_code == 429, response.get_data(as_text=True)
    assert response.json == {'code': 'RATE_LIMIT_EXCEEDED'}
    retry_after = response.headers.get('Retry-After')
    assert retry_after is not None
    assert int(retry_after) >= 1


def test_eleventh_login_from_one_ip_is_429(test_app, test_db, test_client):
    """The 11th auth request from one IP is 429 with Retry-After."""
    _enable_rate_limit(test_app, username_max=100)
    register_user(test_client, username='ipuser', password='testpass8')
    for attempt in range(9):
        response = _login(test_client, 'ipuser', 'wrong-password')
        assert response.status_code == 401, attempt
    eleventh = _login(test_client, 'ipuser', 'wrong-password')
    _assert_rate_limited(eleventh)


def test_eleventh_register_from_one_ip_is_429(test_app, test_db, test_client):
    """Register shares the per-IP auth bucket with login."""
    _enable_rate_limit(test_app)
    for index in range(10):
        response = _register(test_client, f'reg{index}')
        assert response.status_code == 201, index
    eleventh = _register(test_client, 'reg-blocked')
    _assert_rate_limited(eleventh)


def test_rotating_ip_hits_per_username_limit(test_app, test_db, test_client):
    """Wrong passwords on one username trip 429 even when REMOTE_ADDR rotates."""
    _enable_rate_limit(test_app)
    register_user(test_client, username='target', password='testpass8')
    for index in range(5):
        response = _login(
            test_client,
            'Target',
            'wrong-password',
            remote_addr=f'203.0.113.{index + 1}',
        )
        assert response.status_code == 401, index
        assert response.json['code'] == 'INVALID_CREDENTIALS'
    blocked = _login(
        test_client,
        'TARGET',
        'wrong-password',
        remote_addr='203.0.113.99',
    )
    _assert_rate_limited(blocked)


def test_username_limit_does_not_reveal_missing_user(test_app, test_db, test_client):
    """Unknown usernames use the same 429 as existing ones after five failures."""
    _enable_rate_limit(test_app)
    for index in range(5):
        response = _login(
            test_client,
            'nobody-here',
            'wrong-password',
            remote_addr=f'198.51.100.{index + 1}',
        )
        assert response.status_code == 401, index
    blocked = _login(
        test_client,
        'nobody-here',
        'wrong-password',
        remote_addr='198.51.100.99',
    )
    _assert_rate_limited(blocked)


def test_blocked_username_skips_password_check(
    test_app, test_db, test_client, monkeypatch
):
    """A locked-out username is rejected without hashing the password."""
    _enable_rate_limit(test_app)
    register_user(test_client, username='locked', password='testpass8')
    for index in range(5):
        response = _login(
            test_client,
            'locked',
            'wrong-password',
            remote_addr=f'192.0.2.{index + 1}',
        )
        assert response.status_code == 401, index

    called = []

    def _boom(stored, provided):
        called.append(provided)
        return False

    monkeypatch.setattr('backend.api.auth.check_password_hash', _boom)
    blocked = _login(
        test_client,
        'locked',
        'testpass8',
        remote_addr='192.0.2.99',
    )
    _assert_rate_limited(blocked)
    assert called == []


def test_successful_login_resets_username_counter(test_app, test_db, test_client):
    """A successful login clears the per-username failure count."""
    _enable_rate_limit(test_app)
    register_user(test_client, username='resetme', password='testpass8')
    for index in range(4):
        response = _login(
            test_client,
            'resetme',
            'wrong-password',
            remote_addr=f'203.0.113.{10 + index}',
        )
        assert response.status_code == 401, index
    success = _login(
        test_client,
        'resetme',
        'testpass8',
        remote_addr='203.0.113.50',
    )
    assert success.status_code == 200
    for index in range(5):
        response = _login(
            test_client,
            'resetme',
            'wrong-password',
            remote_addr=f'203.0.113.{60 + index}',
        )
        assert response.status_code == 401, index
    blocked = _login(
        test_client,
        'resetme',
        'wrong-password',
        remote_addr='203.0.113.80',
    )
    _assert_rate_limited(blocked)


def _apply_sqlite_pragmas(engine) -> None:
    """Match production WAL / busy-timeout settings on a test engine."""

    @event.listens_for(engine, 'connect')
    def _on_connect(dbapi_conn, _connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute('PRAGMA busy_timeout=30000')
        cursor.execute('PRAGMA journal_mode=WAL')
        cursor.close()


def _rebind_original_db(url: str):
    """Point the original ``backend.db`` singleton (model metadata) at ``url``.

    ``test_bootstrap_db`` may replace ``database.db`` with a new empty Base.
    Models, ``rate_limit``, and ``auth`` keep the first singleton.
    """
    from backend import db
    from backend.api import auth as auth_mod

    old_engine = db._engine
    new_engine = create_engine(
        url,
        connect_args={'check_same_thread': False, 'timeout': 30},
    )
    _apply_sqlite_pragmas(new_engine)
    db._Session.remove()
    db._engine = new_engine
    db._Session.configure(bind=new_engine)
    auth_mod.db_session.bind = new_engine
    db.Base.metadata.create_all(new_engine)
    return old_engine, new_engine


def _restore_original_db(old_engine, new_engine) -> None:
    """Put the original Database singleton back on the fixture engine."""
    from backend import db
    from backend.api import auth as auth_mod

    db._Session.remove()
    db._engine = old_engine
    db._Session.configure(bind=old_engine)
    auth_mod.db_session.bind = old_engine
    new_engine.dispose()


@pytest.fixture
def shared_sqlite_file(tmp_path) -> Iterator[str]:
    """File-backed SQLite shared by two create_app() instances."""
    db_path = tmp_path / 'shared-rate.db'
    url = f'sqlite:///{db_path}'
    old_engine, new_engine = _rebind_original_db(url)
    try:
        yield url
    finally:
        _restore_original_db(old_engine, new_engine)


def test_two_apps_sharing_sqlite_file_trip_limit(shared_sqlite_file):
    """Two create_app() objects sharing one SQLite file share the IP counter.

    After the first app's six hits, any in-process dict is cleared so a
    memory-only limiter cannot leak counts into the second app.
    """
    from backend import create_app
    from backend.api import rate_limit as rate_limit_mod

    app1 = create_app()
    app2 = create_app()
    _enable_rate_limit(app1, username_max=100)
    _enable_rate_limit(app2, username_max=100)

    client1 = app1.test_client()
    client2 = app2.test_client()
    register_user(client1, username='shared', password='testpass8')

    for index in range(5):
        response = _login(client1, 'shared', 'wrong-password')
        assert response.status_code == 401, index

    if hasattr(rate_limit_mod, '_hits'):
        rate_limit_mod._hits.clear()

    statuses = []
    for index in range(6):
        response = _login(client2, 'shared', 'wrong-password')
        statuses.append(response.status_code)
        if response.status_code == 429:
            _assert_rate_limited(response)
            break
    assert 429 in statuses, statuses


def test_sqlite_concurrent_increments_lose_no_counts(tmp_path):
    """Threads hammering one key on two SQLite engines must not drop hits."""
    from backend.api.rate_limit import increment_counter
    from backend.models.rate_limit_counter import RateLimitCounter

    db_path = tmp_path / 'concurrent.db'
    url = f'sqlite:///{db_path}'

    def _engine():
        engine = create_engine(
            url,
            connect_args={'check_same_thread': False, 'timeout': 30},
        )
        _apply_sqlite_pragmas(engine)
        return engine

    setup = _engine()
    RateLimitCounter.__table__.create(setup)

    thread_count = 8
    hits_per_thread = 25
    engines = [_engine() for _ in range(thread_count)]
    errors: list[BaseException] = []

    def _worker(engine) -> None:
        try:
            for _ in range(hits_per_thread):
                count = increment_counter(
                    'auth_ip',
                    '198.51.100.10',
                    window_seconds=60,
                    engine=engine,
                )
                assert count is not None
        except BaseException as exc:  # noqa: BLE001 — surface in parent
            errors.append(exc)

    threads = [threading.Thread(target=_worker, args=(engine,)) for engine in engines]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert errors == []

    with setup.connect() as conn:
        stored = conn.execute(
            text(
                'SELECT hit_count FROM rate_limit_counters '
                "WHERE scope = 'auth_ip' AND key = '198.51.100.10'"
            )
        ).scalar_one()
    assert stored == thread_count * hits_per_thread


def test_trust_proxy_keys_on_rightmost_forwarded_for(test_app, test_db, test_client):
    """With ProxyFix x_for=1, X-Forwarded-For: spoofed, real keys on real."""
    from werkzeug.middleware.proxy_fix import ProxyFix

    _enable_rate_limit(test_app, username_max=100)
    test_app.wsgi_app = ProxyFix(
        test_app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )
    register_user(test_client, username='xffuser', password='testpass8')

    real_headers = {'X-Forwarded-For': '203.0.113.1, 198.51.100.20'}
    other_headers = {'X-Forwarded-For': '203.0.113.1, 198.51.100.30'}
    for index in range(10):
        response = _login(
            test_client,
            'xffuser',
            'wrong-password',
            remote_addr='10.0.0.5',
            extra_headers=real_headers,
        )
        assert response.status_code == 401, index

    other = _login(
        test_client,
        'xffuser',
        'wrong-password',
        remote_addr='10.0.0.5',
        extra_headers=other_headers,
    )
    assert other.status_code == 401

    eleventh = _login(
        test_client,
        'xffuser',
        'wrong-password',
        remote_addr='10.0.0.5',
        extra_headers=real_headers,
    )
    _assert_rate_limited(eleventh)


def test_expired_window_allows_requests_again(
    test_app, test_db, test_client, monkeypatch
):
    """After the IP window elapses, the next request is accepted."""
    from backend.api import rate_limit as rate_limit_mod

    _enable_rate_limit(test_app, username_max=100)
    clock = {'now': 1_700_000_000.0}
    monkeypatch.setattr(rate_limit_mod.time, 'time', lambda: clock['now'])
    register_user(test_client, username='windowed', password='testpass8')
    for index in range(9):
        response = _login(test_client, 'windowed', 'wrong-password')
        assert response.status_code == 401, index
    blocked = _login(test_client, 'windowed', 'wrong-password')
    _assert_rate_limited(blocked)

    clock['now'] += 61
    allowed = _login(test_client, 'windowed', 'wrong-password')
    assert allowed.status_code == 401
    assert allowed.json['code'] == 'INVALID_CREDENTIALS'


def test_store_error_fails_open(test_app, test_db, test_client, monkeypatch):
    """A store write failure logs a warning and still authenticates."""
    from backend.api import rate_limit as rate_limit_mod

    _enable_rate_limit(test_app)
    register_user(test_client, username='openuser', password='testpass8')

    def _boom(*_args, **_kwargs):
        raise RuntimeError('simulated store outage')

    logged: list[str] = []

    def _capture_warning(message, *args, **_kwargs):
        logged.append(message % args if args else str(message))

    monkeypatch.setattr(rate_limit_mod, 'increment_counter', _boom)
    monkeypatch.setattr(rate_limit_mod.logger, 'warning', _capture_warning)
    response = login_user(test_client, username='openuser', password='testpass8')
    assert response.status_code == 200
    assert any(
        'failed open' in line.lower() or 'store' in line.lower() for line in logged
    )


def test_client_ip_key_groups_ipv6_by_slash_64():
    """IPv6 clients in the same /64 share a key; IPv4 stays host-specific."""
    from backend.api.rate_limit import client_ip_key

    assert client_ip_key('192.0.2.10') == '192.0.2.10'
    first = client_ip_key('2001:db8:1:2::1')
    second = client_ip_key('2001:db8:1:2::ffff')
    other = client_ip_key('2001:db8:1:3::1')
    assert first == second
    assert first != other
    assert client_ip_key(None) == 'unknown'
