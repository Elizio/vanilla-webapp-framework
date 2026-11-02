"""Login/register rate-limit behaviour: IP, username, shared SQLite store."""

from __future__ import annotations

import logging
import sqlite3
import threading
import time
from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, event, text

from backend.tests.conftest import csrf_headers, login_user, register_user

_FROZEN_IP = 1_700_000_000.0
_FROZEN_USER = 1_700_000_000.0
_IP_RETRY_AFTER = 40
_USER_RETRY_AFTER = 100


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


def _assert_rate_limited(response, *, retry_after: int | None = None) -> None:
    """Assert the app JSON 429 shape plus Retry-After."""
    assert response.status_code == 429, response.get_data(as_text=True)
    assert response.json == {'code': 'RATE_LIMIT_EXCEEDED'}
    header = response.headers.get('Retry-After')
    assert header is not None
    if retry_after is None:
        assert int(header) >= 1
    else:
        assert int(header) == retry_after


def _freeze_now(monkeypatch, now: float) -> None:
    """Pin the limiter clock via the injectable ``_now`` helper."""
    from backend.api import rate_limit as rate_limit_mod

    monkeypatch.setattr(rate_limit_mod, '_now', lambda: now)


@pytest.fixture(autouse=True)
def _pin_limiter_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep every test off the wall-clock 60s/900s epoch windows.

    Tests that need a moving clock replace ``_now`` in the body.
    """
    _freeze_now(monkeypatch, _FROZEN_IP)


def test_eleventh_login_from_one_ip_is_429(test_app, test_db, test_client, monkeypatch):
    """The 11th auth request from one IP is 429 with Retry-After."""
    _enable_rate_limit(test_app, username_max=100)
    _freeze_now(monkeypatch, _FROZEN_IP)
    register_user(test_client, username='ipuser', password='testpass8')
    for attempt in range(9):
        response = _login(test_client, 'ipuser', 'wrong-password')
        assert response.status_code == 401, attempt
    eleventh = _login(test_client, 'ipuser', 'wrong-password')
    _assert_rate_limited(eleventh)


def test_eleventh_register_from_one_ip_is_429(
    test_app, test_db, test_client, monkeypatch
):
    """Register shares the per-IP auth bucket with login."""
    _enable_rate_limit(test_app)
    _freeze_now(monkeypatch, _FROZEN_IP)
    for index in range(10):
        response = _register(test_client, f'reg{index}')
        assert response.status_code == 201, index
    eleventh = _register(test_client, 'reg-blocked')
    _assert_rate_limited(eleventh)


def test_rotating_ip_hits_per_username_limit(
    test_app, test_db, test_client, monkeypatch
):
    """Wrong passwords on one exact username trip 429 when REMOTE_ADDR rotates."""
    _enable_rate_limit(test_app)
    _freeze_now(monkeypatch, _FROZEN_USER)
    register_user(test_client, username='target', password='testpass8')
    for index in range(5):
        response = _login(
            test_client,
            'target',
            'wrong-password',
            remote_addr=f'203.0.113.{index + 1}',
        )
        assert response.status_code == 401, index
        assert response.json['code'] == 'INVALID_CREDENTIALS'
    blocked = _login(
        test_client,
        'target',
        'wrong-password',
        remote_addr='203.0.113.99',
    )
    _assert_rate_limited(blocked)


def test_username_case_variant_success_does_not_reset_or_clear_lockout(
    test_app, test_db, test_client, monkeypatch
):
    """Lowercase failures stay counted after a case-variant success.

    Registers ``Victim``, fails as ``victim`` four times, then logs in as
    ``Victim``. The sixth ``victim`` failure must still 429 — a lowercase
    store key would have been reset by the ``Victim`` success.
    """
    _enable_rate_limit(test_app)
    _freeze_now(monkeypatch, _FROZEN_USER)
    register_user(test_client, username='Victim', password='testpass8')
    for index in range(4):
        response = _login(
            test_client,
            'victim',
            'wrong-password',
            remote_addr=f'203.0.113.{index + 1}',
        )
        assert response.status_code == 401, index

    success = _login(
        test_client,
        'Victim',
        'testpass8',
        remote_addr='203.0.113.50',
    )
    assert success.status_code == 200

    fifth = _login(
        test_client,
        'victim',
        'wrong-password',
        remote_addr='203.0.113.60',
    )
    assert fifth.status_code == 401
    sixth = _login(
        test_client,
        'victim',
        'wrong-password',
        remote_addr='203.0.113.61',
    )
    _assert_rate_limited(sixth)

    still_ok = _login(
        test_client,
        'Victim',
        'testpass8',
        remote_addr='203.0.113.70',
    )
    assert still_ok.status_code == 200
    still_blocked = _login(
        test_client,
        'victim',
        'wrong-password',
        remote_addr='203.0.113.71',
    )
    _assert_rate_limited(still_blocked)


def test_username_limit_does_not_reveal_missing_user(
    test_app, test_db, test_client, monkeypatch
):
    """Unknown usernames use the same 429 as existing ones after five failures."""
    _enable_rate_limit(test_app)
    _freeze_now(monkeypatch, _FROZEN_USER)
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


def test_unknown_username_still_checks_password_hash(
    test_app, test_db, test_client, monkeypatch
):
    """Missing users still run ``check_password_hash`` (timing-safe dummy)."""
    _enable_rate_limit(test_app)
    called: list[str] = []

    def _capture(stored, provided):
        called.append(stored)
        return False

    monkeypatch.setattr('backend.api.auth.check_password_hash', _capture)
    response = _login(test_client, 'no-such-user', 'whatever')
    assert response.status_code == 401
    assert called


def test_blocked_username_skips_password_check(
    test_app, test_db, test_client, monkeypatch
):
    """A locked-out username is rejected without hashing the password."""
    _enable_rate_limit(test_app)
    _freeze_now(monkeypatch, _FROZEN_USER)
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


def test_successful_login_resets_username_counter(
    test_app, test_db, test_client, monkeypatch
):
    """A successful login clears the per-username failure count."""
    _enable_rate_limit(test_app)
    _freeze_now(monkeypatch, _FROZEN_USER)
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


def test_counters_store_hashed_keys_not_raw_usernames(test_app, test_db, test_client):
    """The counters table stores sha256 hex, never the raw username or IP."""
    from backend.api import rate_limit as rate_limit_mod
    from backend.api.rate_limit import hashed_counter_key

    _enable_rate_limit(test_app)
    register_user(test_client, username='hashuser', password='testpass8')
    stranger = test_app.test_client()
    response = _login(stranger, 'hashuser', 'wrong-password')
    assert response.status_code == 401

    with rate_limit_mod.db.engine.connect() as conn:
        keys = conn.execute(text('SELECT key FROM rate_limit_counters')).scalars().all()
    assert hashed_counter_key('hashuser') in keys
    assert hashed_counter_key('127.0.0.1') in keys
    assert 'hashuser' not in keys
    assert '127.0.0.1' not in keys
    assert all(len(key) == 64 for key in keys)


def _apply_sqlite_pragmas(engine) -> None:
    """Match the app-wide SQLite busy timeout (no WAL)."""

    @event.listens_for(engine, 'connect')
    def _on_connect(dbapi_conn, _connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute('PRAGMA busy_timeout=5000')
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
        connect_args={'check_same_thread': False, 'timeout': 5},
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


def test_two_apps_sharing_sqlite_file_trip_limit(shared_sqlite_file, monkeypatch):
    """Two create_app() objects sharing one SQLite file share the IP counter."""
    from backend import create_app

    _freeze_now(monkeypatch, _FROZEN_IP)
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

    statuses = []
    for index in range(6):
        response = _login(client2, 'shared', 'wrong-password')
        statuses.append(response.status_code)
        if response.status_code == 429:
            _assert_rate_limited(response)
            break
    assert 429 in statuses, statuses


def test_sqlite_concurrent_increments_lose_no_counts(tmp_path, monkeypatch):
    """Threads hammering one key on two SQLite engines must not drop hits."""
    from backend.api.rate_limit import hashed_counter_key, increment_counter
    from backend.models.rate_limit_counter import RateLimitCounter

    _freeze_now(monkeypatch, _FROZEN_IP)

    db_path = tmp_path / 'concurrent.db'
    url = f'sqlite:///{db_path}'

    def _engine():
        engine = create_engine(
            url,
            connect_args={'check_same_thread': False, 'timeout': 5},
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

    digest = hashed_counter_key('198.51.100.10')
    with setup.connect() as conn:
        stored = conn.execute(
            text(
                'SELECT hit_count FROM rate_limit_counters '
                "WHERE scope = 'auth_ip' AND key = :key"
            ),
            {'key': digest},
        ).scalar_one()
    assert stored == thread_count * hits_per_thread


def test_concurrent_logins_cap_password_checks(shared_sqlite_file, monkeypatch):
    """Atomic increment-before-password lets at most 5 concurrent checks run."""
    from backend import create_app

    _freeze_now(monkeypatch, _FROZEN_USER)
    app = create_app()
    _enable_rate_limit(app)
    app.config['RATELIMIT_AUTH_IP_MAX'] = 100
    client = app.test_client()
    register_user(client, username='parallel', password='testpass8')

    calls: list[str] = []
    call_lock = threading.Lock()

    def _slow(stored, provided):
        with call_lock:
            calls.append(provided)
        time.sleep(0.25)
        return False

    monkeypatch.setattr('backend.api.auth.check_password_hash', _slow)

    statuses: list[int] = []
    status_lock = threading.Lock()

    def _worker(index: int) -> None:
        thread_client = app.test_client()
        response = _login(
            thread_client,
            'parallel',
            'wrong-password',
            remote_addr=f'203.0.113.{index + 1}',
        )
        with status_lock:
            statuses.append(response.status_code)

    threads = [threading.Thread(target=_worker, args=(index,)) for index in range(12)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(calls) <= 5, calls
    assert 429 in statuses, statuses


def test_limiter_does_not_commit_pending_orm_writes(shared_sqlite_file):
    """On a file SQLite DB, limiter commits do not flush pending session writes."""
    from backend.api import rate_limit as rate_limit_mod
    from backend.api.rate_limit import (
        AUTH_IP_SCOPE,
        hashed_counter_key,
        increment_counter,
    )
    from backend.models.user import User

    session = rate_limit_mod.db.session
    pending = User(username='pending-user', password_hash='x')
    session.add(pending)
    count = increment_counter(AUTH_IP_SCOPE, '198.51.100.7', 60)
    assert count == 1
    session.rollback()

    assert session.query(User).filter_by(username='pending-user').first() is None
    digest = hashed_counter_key('198.51.100.7')
    with rate_limit_mod.db.engine.connect() as conn:
        stored = conn.execute(
            text('SELECT hit_count FROM rate_limit_counters WHERE key = :key'),
            {'key': digest},
        ).scalar_one()
    assert stored == 1


def test_locked_sqlite_fails_open_within_busy_timeout(
    shared_sqlite_file, caplog, monkeypatch
):
    """A write-locked file DB fail-opens well before gunicorn's 30s timeout."""
    from backend import create_app
    from backend.api import rate_limit as rate_limit_mod
    from backend.api.rate_limit import SQLITE_BUSY_TIMEOUT_MS, STORE_FAILED_OPEN

    app = create_app()
    _enable_rate_limit(app, username_max=100)
    client = app.test_client()
    register_user(client, username='lockuser', password='testpass8')
    logged: list[str] = []
    real_warning = rate_limit_mod.logger.warning

    def _capture(message, *args, **kwargs):
        logged.append(message % args if args else str(message))
        return real_warning(message, *args, **kwargs)

    monkeypatch.setattr(rate_limit_mod.logger, 'warning', _capture)

    db_path = shared_sqlite_file.removeprefix('sqlite:///')
    acquired = threading.Event()

    def _hold_lock() -> None:
        conn = sqlite3.connect(db_path, timeout=0)
        try:
            conn.execute('BEGIN IMMEDIATE')
            acquired.set()
            time.sleep((SQLITE_BUSY_TIMEOUT_MS / 1000) + 0.8)
            conn.rollback()
        finally:
            conn.close()

    holder = threading.Thread(target=_hold_lock)
    holder.start()
    assert acquired.wait(timeout=2)
    try:
        with caplog.at_level(logging.WARNING):
            started = time.monotonic()
            response = _login(client, 'lockuser', 'testpass8')
            elapsed = time.monotonic() - started
    finally:
        holder.join(timeout=10)

    assert response.status_code in (200, 401), response.get_data(as_text=True)
    assert elapsed < 10
    assert any(entry.startswith(STORE_FAILED_OPEN) for entry in logged)


def test_trust_proxy_keys_on_rightmost_forwarded_for(test_db, monkeypatch):
    """TRUST_PROXY=1 + create_app() keys on the rightmost X-Forwarded-For hop."""
    from backend import create_app
    from backend.config.app_config import reset_app_config_for_tests

    monkeypatch.setenv('TRUST_PROXY', '1')
    monkeypatch.setenv('TRUST_PROXY_HOPS', '1')
    reset_app_config_for_tests()
    try:
        app = create_app()
        _enable_rate_limit(app, username_max=100)
        client = app.test_client()
        _freeze_now(monkeypatch, _FROZEN_IP)
        register_user(client, username='xffuser', password='testpass8')

        real_headers = {'X-Forwarded-For': '203.0.113.1, 198.51.100.20'}
        other_headers = {'X-Forwarded-For': '203.0.113.1, 198.51.100.30'}
        for index in range(10):
            response = _login(
                client,
                'xffuser',
                'wrong-password',
                remote_addr='10.0.0.5',
                extra_headers=real_headers,
            )
            assert response.status_code == 401, index

        other = _login(
            client,
            'xffuser',
            'wrong-password',
            remote_addr='10.0.0.5',
            extra_headers=other_headers,
        )
        assert other.status_code == 401

        eleventh = _login(
            client,
            'xffuser',
            'wrong-password',
            remote_addr='10.0.0.5',
            extra_headers=real_headers,
        )
        _assert_rate_limited(eleventh)
    finally:
        monkeypatch.setenv('TRUST_PROXY', '0')
        monkeypatch.delenv('TRUST_PROXY_HOPS', raising=False)
        reset_app_config_for_tests()


def test_expired_window_allows_requests_again(
    test_app, test_db, test_client, monkeypatch
):
    """After the IP window elapses, the next request is accepted."""
    from backend.api import rate_limit as rate_limit_mod

    _enable_rate_limit(test_app, username_max=100)
    clock = {'now': _FROZEN_IP}

    def _clock() -> float:
        return clock['now']

    monkeypatch.setattr(rate_limit_mod, '_now', _clock)
    register_user(test_client, username='windowed', password='testpass8')
    for index in range(9):
        response = _login(test_client, 'windowed', 'wrong-password')
        assert response.status_code == 401, index
    blocked = _login(test_client, 'windowed', 'wrong-password')
    _assert_rate_limited(blocked, retry_after=_IP_RETRY_AFTER)

    clock['now'] += 61
    allowed = _login(test_client, 'windowed', 'wrong-password')
    assert allowed.status_code == 401
    assert allowed.json['code'] == 'INVALID_CREDENTIALS'


def test_username_window_expires(test_app, test_db, test_client, monkeypatch):
    """The per-username window expires independently of the IP window."""
    from backend.api import rate_limit as rate_limit_mod

    _enable_rate_limit(test_app)
    test_app.config['RATELIMIT_AUTH_IP_MAX'] = 100
    clock = {'now': _FROZEN_USER}

    def _clock() -> float:
        return clock['now']

    monkeypatch.setattr(rate_limit_mod, '_now', _clock)
    register_user(test_client, username='userwindow', password='testpass8')
    for index in range(5):
        response = _login(
            test_client,
            'userwindow',
            'wrong-password',
            remote_addr=f'198.51.100.{index + 1}',
        )
        assert response.status_code == 401, index
    blocked = _login(
        test_client,
        'userwindow',
        'wrong-password',
        remote_addr='198.51.100.99',
    )
    _assert_rate_limited(blocked, retry_after=_USER_RETRY_AFTER)

    clock['now'] += 901
    allowed = _login(
        test_client,
        'userwindow',
        'wrong-password',
        remote_addr='198.51.100.80',
    )
    assert allowed.status_code == 401
    assert allowed.json['code'] == 'INVALID_CREDENTIALS'


def test_ip_retry_after_matches_frozen_clock(
    test_app, test_db, test_client, monkeypatch
):
    """Retry-After is the remaining seconds of the frozen IP window."""
    _enable_rate_limit(test_app, username_max=100)
    _freeze_now(monkeypatch, _FROZEN_IP)
    register_user(test_client, username='retryip', password='testpass8')
    for index in range(9):
        response = _login(test_client, 'retryip', 'wrong-password')
        assert response.status_code == 401, index
    blocked = _login(test_client, 'retryip', 'wrong-password')
    _assert_rate_limited(blocked, retry_after=_IP_RETRY_AFTER)


def test_store_error_fails_open(test_app, test_db, test_client, caplog, monkeypatch):
    """Dropping the counters table fail-opens with the exact warning text."""
    from backend.api import rate_limit as rate_limit_mod
    from backend.api.rate_limit import STORE_FAILED_OPEN
    from backend.models.rate_limit_counter import RateLimitCounter

    _enable_rate_limit(test_app)
    register_user(test_client, username='openuser', password='testpass8')
    RateLimitCounter.__table__.drop(rate_limit_mod.db.engine)

    logged: list[str] = []
    real_warning = rate_limit_mod.logger.warning

    def _capture(message, *args, **kwargs):
        logged.append(message % args if args else str(message))
        return real_warning(message, *args, **kwargs)

    monkeypatch.setattr(rate_limit_mod.logger, 'warning', _capture)
    with caplog.at_level(logging.WARNING):
        response = login_user(test_client, username='openuser', password='testpass8')
    assert response.status_code == 200
    assert any(entry.startswith(STORE_FAILED_OPEN) for entry in logged)


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


def test_username_key_is_exact_stripped_value():
    """Username keys strip whitespace but keep case."""
    from backend.api.rate_limit import username_key

    assert username_key('  Victim  ') == 'Victim'
    assert username_key('victim') == 'victim'
    assert username_key('Victim') != username_key('victim')


def test_client_subnet_key_groups_ipv4_slash_24():
    """Untrusted pair keys group IPv4 by /24 and IPv6 by /64."""
    from backend.api.rate_limit import client_subnet_key

    assert client_subnet_key('203.0.113.10') == client_subnet_key('203.0.113.99')
    assert client_subnet_key('203.0.113.10') != client_subnet_key('203.0.114.10')
    first = client_subnet_key('2001:db8:1:2::1')
    second = client_subnet_key('2001:db8:1:2::ffff')
    other = client_subnet_key('2001:db8:1:3::1')
    assert first == second
    assert first != other
    assert client_subnet_key(None) == 'unknown'


def _device_cookie_value(client) -> str:
    """Return the ``auth_device`` cookie value from a test client jar."""
    from backend.api.rate_limit import DEVICE_COOKIE_NAME

    cookie = client.get_cookie(DEVICE_COOKIE_NAME)
    assert cookie is not None
    return cookie.value


def _itsdangerous_parts(token: str) -> tuple[str, str, str]:
    """Split an itsdangerous token into payload, timestamp, and signature.

    Compressed payloads are prefixed with ``.``, so this uses ``rsplit``.
    """
    payload, timestamp, signature = token.rsplit('.', 2)
    assert payload and timestamp and signature, token
    return payload, timestamp, signature


def _flip_middle_char(text: str) -> str:
    """Return ``text`` with the middle character changed deterministically."""
    assert text
    mid = len(text) // 2
    flip = 'A' if text[mid] != 'A' else 'B'
    return f'{text[:mid]}{flip}{text[mid + 1 :]}'


def _untrusted_device_cookie(kind: str, real_device: str, bob_device: str) -> str:
    """Return a cookie that must not authenticate as Alice's device.

    Args:
        kind: ``forged_signature``, ``tampered_payload``,
            ``truncated_signature``, or ``foreign``.
        real_device: Alice's signed cookie.
        bob_device: Bob's signed cookie.
    """
    if kind == 'foreign':
        return bob_device
    payload, timestamp, signature = _itsdangerous_parts(real_device)
    if kind == 'forged_signature':
        signature = _flip_middle_char(signature)
    elif kind == 'tampered_payload':
        payload = _flip_middle_char(payload)
    elif kind == 'truncated_signature':
        signature = signature[: max(1, len(signature) // 2)]
    else:
        raise AssertionError(f'unknown cookie kind {kind}')
    return f'{payload}.{timestamp}.{signature}'


def test_device_cookie_allows_login_after_rotating_ip_attack(
    test_app, test_db, test_client, monkeypatch
):
    """Alice with her device cookie logs in after untrusted IPs exhaust limits."""
    from backend.api.rate_limit import DEVICE_COOKIE_NAME

    _enable_rate_limit(test_app)
    test_app.config['RATELIMIT_AUTH_IP_MAX'] = 100
    _freeze_now(monkeypatch, 1_699_999_200.0)
    register_user(test_client, username='alice', password='testpass8')
    device_value = _device_cookie_value(test_client)

    for index in range(20):
        attacker = test_app.test_client()
        response = _login(
            attacker,
            'alice',
            'wrong-password',
            remote_addr=f'203.0.{index}.10',
        )
        assert response.status_code in (401, 429), index

    alice = test_app.test_client()
    alice.set_cookie(DEVICE_COOKIE_NAME, device_value)
    success = _login(alice, 'alice', 'testpass8', remote_addr='198.51.100.8')
    assert success.status_code == 200


def test_untrusted_clean_ip_is_delayed_not_permanently_blocked(
    test_app, test_db, test_client, monkeypatch
):
    """An untrusted new subnet is delayed up to the cap, never locked out."""
    from backend.api import rate_limit as rate_limit_mod
    from backend.api.rate_limit import LOGIN_BACKOFF_CAP_SECONDS

    _enable_rate_limit(test_app)
    test_app.config['RATELIMIT_AUTH_IP_MAX'] = 100
    clock = {'now': 1_699_999_200.0}

    def _clock() -> float:
        return clock['now']

    monkeypatch.setattr(rate_limit_mod, '_now', _clock)
    register_user(test_client, username='alice', password='testpass8')

    saw_backoff = False
    for index in range(20):
        attacker = test_app.test_client()
        response = _login(
            attacker,
            'alice',
            'wrong-password',
            remote_addr=f'198.51.{index}.10',
        )
        if response.status_code == 429:
            retry = int(response.headers['Retry-After'])
            assert 1 <= retry <= LOGIN_BACKOFF_CAP_SECONDS
            saw_backoff = True
        else:
            assert response.status_code == 401, index
    assert saw_backoff

    clean = test_app.test_client()
    blocked = _login(clean, 'alice', 'wrong-password', remote_addr='192.0.2.50')
    _assert_rate_limited(blocked)
    retry = int(blocked.headers['Retry-After'])
    assert retry <= LOGIN_BACKOFF_CAP_SECONDS
    clock['now'] += retry
    allowed = _login(clean, 'alice', 'wrong-password', remote_addr='192.0.2.50')
    assert allowed.status_code == 401
    assert allowed.json['code'] == 'INVALID_CREDENTIALS'


def test_rotating_ip_brute_force_password_checks_stay_bounded(
    test_app, test_db, test_client, monkeypatch
):
    """Untrusted rotating-IP guesses stay at the documented per-window bound."""
    from backend.api import rate_limit as rate_limit_mod
    from backend.api.rate_limit import UNTRUSTED_PASSWORD_CHECKS_PER_WINDOW

    _enable_rate_limit(test_app)
    test_app.config['RATELIMIT_AUTH_IP_MAX'] = 200
    clock = {'now': 1_699_999_200.0}

    def _clock() -> float:
        return clock['now']

    monkeypatch.setattr(rate_limit_mod, '_now', _clock)
    register_user(test_client, username='target', password='testpass8')

    calls: list[str] = []

    def _capture(stored, provided):
        calls.append(provided)
        return False

    monkeypatch.setattr('backend.api.auth.check_password_hash', _capture)

    deadline = clock['now'] + 900
    index = 0
    while clock['now'] < deadline and index < 40:
        attacker = test_app.test_client()
        response = _login(
            attacker,
            'target',
            'wrong-password',
            remote_addr=f'10.{index}.0.1',
        )
        index += 1
        if response.status_code == 429:
            clock['now'] += int(response.headers['Retry-After'])
            continue
        assert response.status_code == 401, response.status_code

    assert len(calls) <= UNTRUSTED_PASSWORD_CHECKS_PER_WINDOW
    assert len(calls) >= 5


@pytest.mark.parametrize(
    'cookie_kind',
    ('forged_signature', 'tampered_payload', 'truncated_signature', 'foreign'),
)
def test_forged_and_foreign_device_cookies_are_untrusted(
    test_app, test_db, test_client, monkeypatch, cookie_kind: str
):
    """Tampered or other-user device cookies do not bypass global backoff.

    A last-character signature tweak is not a forgery: trailing base64
    alphabet neighbors can decode to the same bytes (~5% still verify).
    """
    from backend.api.rate_limit import DEVICE_COOKIE_NAME

    _enable_rate_limit(test_app)
    test_app.config['RATELIMIT_AUTH_IP_MAX'] = 100
    _freeze_now(monkeypatch, 1_699_999_200.0)
    register_user(test_client, username='alice', password='testpass8')
    real_device = _device_cookie_value(test_client)

    bob = test_app.test_client()
    register_user(bob, username='bob', password='testpass8')
    bob_device = _device_cookie_value(bob)
    bad_value = _untrusted_device_cookie(cookie_kind, real_device, bob_device)

    for index in range(20):
        attacker = test_app.test_client()
        response = _login(
            attacker,
            'alice',
            'wrong-password',
            remote_addr=f'203.0.{index}.20',
        )
        assert response.status_code in (401, 429), index

    impostor = test_app.test_client()
    impostor.set_cookie(DEVICE_COOKIE_NAME, bad_value)
    blocked = _login(impostor, 'alice', 'testpass8', remote_addr='198.51.100.40')
    assert blocked.status_code == 429, (
        f'{cookie_kind} device cookie was trusted for alice: '
        f'{blocked.get_data(as_text=True)}'
    )
    _assert_rate_limited(blocked)

    alice = test_app.test_client()
    alice.set_cookie(DEVICE_COOKIE_NAME, real_device)
    success = _login(alice, 'alice', 'testpass8', remote_addr='192.0.2.9')
    assert success.status_code == 200
