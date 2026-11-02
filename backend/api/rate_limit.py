"""Shared-database rate limiting for login and register."""

from __future__ import annotations

import hashlib
import ipaddress
import logging
import secrets
import time
from functools import wraps
from typing import Any, Callable, Mapping

from flask import Response, current_app, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy import text
from sqlalchemy.engine import Engine

from backend.db_repository.database import db
from backend.models.rate_limit_counter import RateLimitCounter

from ..config.cookie_names import LEGACY_DEVICE_COOKIE_NAME
from .cookie_path import (
    app_cookie_path,
    cookie_secure,
    device_cookie_name,
    expire_legacy_root_cookie,
    expire_replaced_cookie,
)
from .error_codes import RATE_LIMIT_EXCEEDED, error_response

logger = logging.getLogger(__name__)

AUTH_IP_SCOPE = 'auth_ip'
LOGIN_USER_SCOPE = 'login_user'
LOGIN_PAIR_SCOPE = 'login_pair'
LOGIN_DEVICE_SCOPE = 'login_device'
LOGIN_USER_TS_SCOPE = 'login_user_ts'
_COUNTER_TABLE = RateLimitCounter.__tablename__
STORE_FAILED_OPEN = 'Rate limit store failed open'
SQLITE_BUSY_TIMEOUT_MS = 3000
LOGIN_BACKOFF_BASE_SECONDS = 2
LOGIN_BACKOFF_CAP_SECONDS = 180
# 5 free + 2+4+8+16+32+64+128 + 3×180 = 15 untrusted password checks / 900 s.
UNTRUSTED_PASSWORD_CHECKS_PER_WINDOW = 15
DEVICE_COOKIE_TTL = 30 * 24 * 3600
DEVICE_COOKIE_SALT = 'auth-device-v1'


def _upsert_sql(values_sql: str) -> str:
    return (
        f'INSERT INTO {_COUNTER_TABLE} '
        '(scope, key, window_start, hit_count, expires_at) '
        f'VALUES ({values_sql}) '
        'ON CONFLICT (scope, key, window_start) DO UPDATE SET '
        f'hit_count = {_COUNTER_TABLE}.hit_count + 1 '
        'RETURNING hit_count'
    )


_UPSERT_NAMED = _upsert_sql(':scope, :key, :window_start, 1, :expires_at')
_UPSERT_QMARK = _upsert_sql('?, ?, ?, 1, ?')
_RESET_SQL = f'DELETE FROM {_COUNTER_TABLE} WHERE scope = :scope AND key = :key'
_PRUNE_SQL = f'DELETE FROM {_COUNTER_TABLE} WHERE expires_at <= :now'
_SELECT_COUNT_SQL = (
    f'SELECT hit_count FROM {_COUNTER_TABLE} '
    'WHERE scope = :scope AND key = :key AND window_start = :window_start'
)
_SET_TS_SQL = (
    f'INSERT INTO {_COUNTER_TABLE} '
    '(scope, key, window_start, hit_count, expires_at) '
    'VALUES (:scope, :key, 0, :hit_count, :expires_at) '
    'ON CONFLICT (scope, key, window_start) DO UPDATE SET '
    'hit_count = :hit_count, expires_at = :expires_at'
)


def _now() -> float:
    """Return the current Unix time (tests replace this, not ``time.time``)."""
    return time.time()


def hashed_counter_key(key: str) -> str:
    """Return the SHA-256 hex digest stored in ``rate_limit_counters.key``.

    Args:
        key: Logical key (client IP grouping, exact username, or pair).

    Returns:
        64-character hex digest.
    """
    return hashlib.sha256(key.encode('utf-8')).hexdigest()


def client_ip_key(remote_addr: str | None) -> str:
    """Return the rate-limit key for a client address.

    IPv4 stays a host address. IPv6 is grouped by the containing /64.
    IPv4-mapped IPv6 addresses collapse to IPv4.

    Args:
        remote_addr: ``request.remote_addr`` or a raw address string.

    Returns:
        A stable key, or ``unknown`` when the address is missing.
    """
    if not remote_addr:
        return 'unknown'
    host = remote_addr.split('%', 1)[0].strip()
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return host or 'unknown'
    if ip.version == 4:
        return str(ip)
    mapped = ip.ipv4_mapped
    if mapped is not None:
        return str(mapped)
    network = ipaddress.ip_network(f'{ip}/64', strict=False)
    return str(network)


def client_subnet_key(remote_addr: str | None) -> str:
    """Return the username-pair subnet key for a client address.

    IPv4 is grouped by /24, IPv6 by /64. IPv4-mapped IPv6 collapses to IPv4.

    Args:
        remote_addr: ``request.remote_addr`` or a raw address string.

    Returns:
        A network string, or ``unknown`` when the address is missing.
    """
    if not remote_addr:
        return 'unknown'
    host = remote_addr.split('%', 1)[0].strip()
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return host or 'unknown'
    if ip.version == 4:
        return str(ipaddress.ip_network(f'{ip}/24', strict=False))
    mapped = ip.ipv4_mapped
    if mapped is not None:
        return str(ipaddress.ip_network(f'{mapped}/24', strict=False))
    return str(ipaddress.ip_network(f'{ip}/64', strict=False))


def username_key(username: str) -> str:
    """Return the exact stripped username used for login lookup.

    Args:
        username: Raw username from the request body.

    Returns:
        ``username.strip()`` — not lowercased, matching ``User.username``.
    """
    return username.strip()


def pair_logical_key(username: str, extra: str) -> str:
    """Return the logical key for a username plus subnet or device id.

    Args:
        username: Exact stripped username.
        extra: Client subnet or device identifier.

    Returns:
        A NUL-separated logical key (hashed before storage).
    """
    return f'{username}\0{extra}'


def increment_counter(
    scope: str,
    key: str,
    window_seconds: int,
    *,
    now: float | None = None,
    engine: Engine | None = None,
) -> int | None:
    """Atomically increment the ``(scope, key, window)`` counter.

    Uses ``INSERT ... ON CONFLICT DO UPDATE ... RETURNING`` so two
    workers sharing SQLite or Postgres cannot lose hits. Expired rows
    are pruned opportunistically in the same short transaction.

    Args:
        scope: Bucket family (``auth_ip``, ``login_pair``, or ``login_device``).
        key: Logical client IP key, pair, or device key.
        window_seconds: Fixed-window length.
        now: Unix timestamp override for tests.
        engine: Optional SQLAlchemy engine (defaults to the app engine).

    Returns:
        The new count, or ``None`` when the store write fails (fail-open).
    """
    try:
        return _atomic_hit(scope, key, window_seconds, now=now, engine=engine)
    except Exception as exc:
        _log_store_failure(exc)
        return None


def reset_counter(
    scope: str,
    key: str,
    *,
    engine: Engine | None = None,
) -> None:
    """Delete every window for ``(scope, key)``.

    Args:
        scope: Bucket family.
        key: Logical client IP key, pair, or device key.
        engine: Optional SQLAlchemy engine.

    Fail-open: a delete error is logged and swallowed.
    """
    bind = engine if engine is not None else db.engine
    try:
        with bind.connect() as conn:
            conn.execute(
                text(_RESET_SQL),
                {'scope': scope, 'key': hashed_counter_key(key)},
            )
            conn.commit()
    except Exception as exc:
        _log_store_failure(exc)


def rate_limit_auth(func: Callable[..., Any]) -> Callable[..., Any]:
    """Limit login and register to N requests per window per client IP."""

    @wraps(func)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        if not current_app.config.get('RATELIMIT_ENABLED', True):
            return func(*args, **kwargs)
        max_hits = int(current_app.config.get('RATELIMIT_AUTH_IP_MAX', 10))
        window = int(current_app.config.get('RATELIMIT_AUTH_IP_WINDOW_SECONDS', 60))
        key = client_ip_key(request.remote_addr)
        count = increment_counter(AUTH_IP_SCOPE, key, window)
        if count is None:
            return func(*args, **kwargs)
        if count > max_hits:
            return _limit_response(_retry_after(window))
        return func(*args, **kwargs)

    return decorated


def username_login_blocked(username: str) -> tuple[Response, int] | None:
    """Gate a login attempt; increment before the password check.

    Trusted device cookies skip the global username backoff and the
    subnet pair. They use a strict per-(username, device) limit.
    Untrusted clients get a hard per-(username, subnet) limit plus a
    global per-username backoff that never permanently locks the
    account.

    Args:
        username: Raw username from the request body.

    Returns:
        The JSON 429 tuple, or ``None`` when the attempt may proceed.
    """
    if not current_app.config.get('RATELIMIT_ENABLED', True):
        return None
    max_hits = int(current_app.config.get('RATELIMIT_LOGIN_USER_MAX', 5))
    window = int(current_app.config.get('RATELIMIT_LOGIN_USER_WINDOW_SECONDS', 900))
    name = username_key(username)
    device_id = trusted_device_id(name)
    if device_id is not None:
        count = increment_counter(
            LOGIN_DEVICE_SCOPE, pair_logical_key(name, device_id), window
        )
        if count is None:
            return None
        if count > max_hits:
            return _limit_response(_retry_after(window))
        return None

    subnet = client_subnet_key(request.remote_addr)
    pair_count = increment_counter(
        LOGIN_PAIR_SCOPE, pair_logical_key(name, subnet), window
    )
    if pair_count is None:
        return None
    if pair_count > max_hits:
        return _limit_response(_retry_after(window))

    reserved = reserve_global_username_slot(name, window, max_hits)
    if reserved is None:
        return None
    _count, retry_after = reserved
    if retry_after is not None:
        return _limit_response(retry_after)
    return None


def reset_failed_logins(username: str) -> None:
    """Clear pair or device counters for this client after success.

    Does not reset the global per-username backoff counter, so an
    attacker cannot clear it by logging into a case-variant account.

    Args:
        username: Raw username from the request body (same string as lookup).
    """
    if not current_app.config.get('RATELIMIT_ENABLED', True):
        return
    name = username_key(username)
    device_id = trusted_device_id(name)
    if device_id is not None:
        reset_counter(LOGIN_DEVICE_SCOPE, pair_logical_key(name, device_id))
        return
    subnet = client_subnet_key(request.remote_addr)
    reset_counter(LOGIN_PAIR_SCOPE, pair_logical_key(name, subnet))


def reserve_global_username_slot(
    username: str,
    window_seconds: int,
    free_hits: int,
    *,
    now: float | None = None,
    engine: Engine | None = None,
) -> tuple[int, int | None] | None:
    """Take a global untrusted slot or return the backoff ``Retry-After``.

    Increments only when the slot is granted, so concurrent requests
    cannot all pass the password check. Too-soon probes do not consume
    a slot.

    Args:
        username: Exact stripped username.
        window_seconds: Fixed-window length.
        free_hits: Immediate attempts allowed before backoff starts.
        now: Unix timestamp override for tests.
        engine: Optional SQLAlchemy engine.

    Returns:
        ``(count, None)`` when the attempt may proceed, ``(count, retry)``
        when it must wait, or ``None`` on store failure (fail-open).
    """
    try:
        return _atomic_reserve_global(
            username,
            window_seconds,
            free_hits,
            now=now,
            engine=engine,
        )
    except Exception as exc:
        _log_store_failure(exc)
        return None


def trusted_device_id(username: str) -> str | None:
    """Return the device id when the request cookie matches ``username``.

    Args:
        username: Exact stripped username.

    Returns:
        The device id, or ``None`` when missing, expired, forged, or bound
        to a different username.
    """
    payload = read_device_cookie()
    if payload is None:
        return None
    if payload['u'] != hashed_counter_key(username_key(username)):
        return None
    return payload['d']


def _parse_device_cookie(raw: str | None) -> dict[str, str] | None:
    """Return a verified device-cookie payload from one cookie value."""
    if not raw:
        return None
    try:
        data = _device_serializer().loads(raw, max_age=DEVICE_COOKIE_TTL)
    except (BadSignature, SignatureExpired, TypeError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    user_hash = data.get('u')
    device_id = data.get('d')
    if not isinstance(user_hash, str) or not isinstance(device_id, str):
        return None
    if not user_hash or not device_id:
        return None
    return {'u': user_hash, 'd': device_id}


def read_device_cookie() -> dict[str, str] | None:
    """Return the verified device-cookie payload, or ``None``.

    Prefers the live namespaced cookie, then the legacy ``auth_device``
    name so sessions survive one deploy. Remove the legacy read after
    ``REFRESH_TOKEN_TTL_DAYS`` plus 7 days; keep expiring the old name.

    Returns:
        ``{'u': username_hash, 'd': device_id}`` when the signature and
        TTL are valid.
    """
    for name in (device_cookie_name(), LEGACY_DEVICE_COOKIE_NAME):
        parsed = _parse_device_cookie(request.cookies.get(name))
        if parsed is not None:
            return parsed
    return None


def issue_device_cookie(response: Response, username: str) -> Response:
    """Set a signed device cookie bound to the exact username.

    Reuses the existing device id when the request already has a valid
    cookie for this username; otherwise mints a new id. HttpOnly,
    SameSite=Lax, Secure in production, same Path as auth cookies.

    Args:
        response: Flask response to mutate.
        username: Exact username just authenticated.

    Returns:
        The same response with ``Set-Cookie`` applied.
    """
    name = username_key(username)
    user_hash = hashed_counter_key(name)
    existing = read_device_cookie()
    device_id = (
        existing['d']
        if existing is not None and existing['u'] == user_hash
        else secrets.token_urlsafe(16)
    )
    token = _device_serializer().dumps({'u': user_hash, 'd': device_id})
    live_name = device_cookie_name()
    response.set_cookie(
        live_name,
        token,
        httponly=True,
        secure=cookie_secure(),
        samesite='Lax',
        path=app_cookie_path(),
        max_age=DEVICE_COOKIE_TTL,
    )
    expire_legacy_root_cookie(response, live_name, httponly=True)
    if live_name != LEGACY_DEVICE_COOKIE_NAME:
        expire_replaced_cookie(response, LEGACY_DEVICE_COOKIE_NAME, httponly=True)
    return response


def _device_serializer() -> URLSafeTimedSerializer:
    secret = current_app.secret_key
    if not secret:
        raise RuntimeError('FLASK_SECRET is required to sign device cookies')
    return URLSafeTimedSerializer(str(secret), salt=DEVICE_COOKIE_SALT)


def _backoff_seconds(next_over: int) -> int:
    if next_over <= 0:
        return 0
    shift = next_over - 1
    if shift >= 31:
        return LOGIN_BACKOFF_CAP_SECONDS
    return min(LOGIN_BACKOFF_CAP_SECONDS, LOGIN_BACKOFF_BASE_SECONDS << shift)


def _window_start(now: float, window_seconds: int) -> int:
    now_i = int(now)
    return now_i - (now_i % window_seconds)


def _retry_after(window_seconds: int, now: float | None = None) -> int:
    clock = _now() if now is None else now
    remaining = _window_start(clock, window_seconds) + window_seconds - int(clock)
    return max(1, remaining)


def _limit_response(retry_after: int) -> tuple[Response, int]:
    response, status = error_response(
        RATE_LIMIT_EXCEEDED,
        429,
        headers={'Retry-After': str(retry_after)},
    )
    return response, status


def _log_store_failure(exc: BaseException) -> None:
    message = f'{STORE_FAILED_OPEN}: %s'
    logger.warning(message, exc)
    try:
        current_app.logger.warning(message, exc)
    except Exception:
        pass


def _should_prune(count: int, now: int) -> bool:
    return count == 1 or (now & 0xF) == 0


def _atomic_hit(
    scope: str,
    key: str,
    window_seconds: int,
    *,
    now: float | None,
    engine: Engine | None,
) -> int:
    clock = _now() if now is None else now
    window_start = _window_start(clock, window_seconds)
    params = {
        'scope': scope,
        'key': hashed_counter_key(key),
        'window_start': window_start,
        'expires_at': window_start + window_seconds,
        'now': int(clock),
    }
    bind = engine if engine is not None else db.engine
    if bind.dialect.name == 'sqlite':
        return _atomic_hit_sqlite(bind, params)
    return _atomic_hit_sql(bind, params)


def _atomic_reserve_global(
    username: str,
    window_seconds: int,
    free_hits: int,
    *,
    now: float | None,
    engine: Engine | None,
) -> tuple[int, int | None]:
    clock = _now() if now is None else now
    window_start = _window_start(clock, window_seconds)
    params = {
        'scope': LOGIN_USER_SCOPE,
        'key': hashed_counter_key(username),
        'window_start': window_start,
        'expires_at': window_start + window_seconds,
        'now': int(clock),
        'ts_scope': LOGIN_USER_TS_SCOPE,
        'ts_expires': int(clock) + window_seconds + LOGIN_BACKOFF_CAP_SECONDS,
        'free_hits': free_hits,
        'window_seconds': window_seconds,
    }
    bind = engine if engine is not None else db.engine
    if bind.dialect.name == 'sqlite':
        return _atomic_reserve_sqlite(bind, params)
    return _atomic_reserve_sql(bind, params)


def _grant_from_state(
    count: int, old_ts: int | None, now: int, free_hits: int
) -> int | None:
    """Return Retry-After seconds, or ``None`` when the slot may be granted."""
    if count < free_hits or old_ts is None:
        return None
    delay = _backoff_seconds(count - free_hits + 1)
    if now >= old_ts + delay:
        return None
    return max(1, min(LOGIN_BACKOFF_CAP_SECONDS, old_ts + delay - now))


def _atomic_hit_sqlite(engine: Engine, params: Mapping[str, Any]) -> int:
    raw = engine.raw_connection()
    old_iso = getattr(raw, 'isolation_level', None)
    try:
        setattr(raw, 'isolation_level', None)
        cursor = raw.cursor()
        try:
            cursor.execute(f'PRAGMA busy_timeout={SQLITE_BUSY_TIMEOUT_MS}')
            cursor.execute('BEGIN IMMEDIATE')
            cursor.execute(
                _UPSERT_QMARK,
                (
                    params['scope'],
                    params['key'],
                    params['window_start'],
                    params['expires_at'],
                ),
            )
            row = cursor.fetchone()
            if row is None:
                raise RuntimeError('rate-limit upsert returned no row')
            count = int(row[0])
            if _should_prune(count, int(params['now'])):
                cursor.execute(
                    f'DELETE FROM {_COUNTER_TABLE} WHERE expires_at <= ?',
                    (params['now'],),
                )
            raw.commit()
            return count
        except Exception:
            raw.rollback()
            raise
        finally:
            cursor.close()
    finally:
        if old_iso is not None:
            try:
                setattr(raw, 'isolation_level', old_iso)
            except Exception:
                pass
        raw.close()


def _atomic_reserve_sqlite(
    engine: Engine, params: Mapping[str, Any]
) -> tuple[int, int | None]:
    raw = engine.raw_connection()
    old_iso = getattr(raw, 'isolation_level', None)
    try:
        setattr(raw, 'isolation_level', None)
        cursor = raw.cursor()
        try:
            cursor.execute(f'PRAGMA busy_timeout={SQLITE_BUSY_TIMEOUT_MS}')
            cursor.execute('BEGIN IMMEDIATE')
            cursor.execute(
                f'SELECT hit_count FROM {_COUNTER_TABLE} '
                'WHERE scope = ? AND key = ? AND window_start = ?',
                (params['scope'], params['key'], params['window_start']),
            )
            row = cursor.fetchone()
            count = int(row[0]) if row is not None else 0
            cursor.execute(
                f'SELECT hit_count FROM {_COUNTER_TABLE} '
                'WHERE scope = ? AND key = ? AND window_start = 0',
                (params['ts_scope'], params['key']),
            )
            ts_row = cursor.fetchone()
            old_ts = int(ts_row[0]) if ts_row is not None else None
            retry = _grant_from_state(
                count, old_ts, int(params['now']), int(params['free_hits'])
            )
            if retry is not None:
                raw.commit()
                return count, retry
            cursor.execute(
                _UPSERT_QMARK,
                (
                    params['scope'],
                    params['key'],
                    params['window_start'],
                    params['expires_at'],
                ),
            )
            granted = cursor.fetchone()
            if granted is None:
                raise RuntimeError('rate-limit upsert returned no row')
            new_count = int(granted[0])
            cursor.execute(
                f'INSERT INTO {_COUNTER_TABLE} '
                '(scope, key, window_start, hit_count, expires_at) '
                'VALUES (?, ?, 0, ?, ?) '
                'ON CONFLICT (scope, key, window_start) DO UPDATE SET '
                'hit_count = excluded.hit_count, expires_at = excluded.expires_at',
                (
                    params['ts_scope'],
                    params['key'],
                    int(params['now']),
                    params['ts_expires'],
                ),
            )
            if _should_prune(new_count, int(params['now'])):
                cursor.execute(
                    f'DELETE FROM {_COUNTER_TABLE} WHERE expires_at <= ?',
                    (params['now'],),
                )
            raw.commit()
            return new_count, None
        except Exception:
            raw.rollback()
            raise
        finally:
            cursor.close()
    finally:
        if old_iso is not None:
            try:
                setattr(raw, 'isolation_level', old_iso)
            except Exception:
                pass
        raw.close()


def _atomic_hit_sql(engine: Engine, params: Mapping[str, Any]) -> int:
    with engine.connect() as conn:
        count = int(conn.execute(text(_UPSERT_NAMED), dict(params)).scalar_one())
        if _should_prune(count, int(params['now'])):
            conn.execute(text(_PRUNE_SQL), {'now': params['now']})
        conn.commit()
        return count


def _atomic_reserve_sql(
    engine: Engine, params: Mapping[str, Any]
) -> tuple[int, int | None]:
    with engine.connect() as conn:
        existing = conn.execute(
            text(_SELECT_COUNT_SQL),
            {
                'scope': params['scope'],
                'key': params['key'],
                'window_start': params['window_start'],
            },
        ).scalar()
        count = int(existing) if existing is not None else 0
        ts_existing = conn.execute(
            text(_SELECT_COUNT_SQL),
            {
                'scope': params['ts_scope'],
                'key': params['key'],
                'window_start': 0,
            },
        ).scalar()
        old_ts = int(ts_existing) if ts_existing is not None else None
        retry = _grant_from_state(
            count, old_ts, int(params['now']), int(params['free_hits'])
        )
        if retry is not None:
            conn.commit()
            return count, retry
        new_count = int(conn.execute(text(_UPSERT_NAMED), dict(params)).scalar_one())
        conn.execute(
            text(_SET_TS_SQL),
            {
                'scope': params['ts_scope'],
                'key': params['key'],
                'hit_count': int(params['now']),
                'expires_at': params['ts_expires'],
            },
        )
        if _should_prune(new_count, int(params['now'])):
            conn.execute(text(_PRUNE_SQL), {'now': params['now']})
        conn.commit()
        return new_count, None
