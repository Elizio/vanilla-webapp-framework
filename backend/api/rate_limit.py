"""Shared-database rate limiting for login and register."""

from __future__ import annotations

import ipaddress
import logging
import time
from functools import wraps
from typing import Any, Callable, Mapping

from flask import Response, current_app, request
from sqlalchemy import text
from sqlalchemy.engine import Engine

from backend.db_repository.database import db
from backend.models.rate_limit_counter import RateLimitCounter

from .error_codes import RATE_LIMIT_EXCEEDED, error_response

logger = logging.getLogger(__name__)

AUTH_IP_SCOPE = 'auth_ip'
LOGIN_USER_SCOPE = 'login_user'
_COUNTER_TABLE = RateLimitCounter.__tablename__

_UPSERT_SQL = (
    f'INSERT INTO {_COUNTER_TABLE} '
    '(scope, key, window_start, hit_count, expires_at) '
    'VALUES (:scope, :key, :window_start, 1, :expires_at) '
    'ON CONFLICT (scope, key, window_start) DO UPDATE SET '
    f'hit_count = {_COUNTER_TABLE}.hit_count + 1 '
    'RETURNING hit_count'
)
_PEEK_SQL = (
    f'SELECT hit_count FROM {_COUNTER_TABLE} '
    'WHERE scope = :scope AND key = :key '
    'AND window_start = :window_start AND expires_at > :now'
)
_RESET_SQL = f'DELETE FROM {_COUNTER_TABLE} WHERE scope = :scope AND key = :key'
_PRUNE_SQL = f'DELETE FROM {_COUNTER_TABLE} WHERE expires_at <= :now'

_SQLITE_UPSERT = (
    f'INSERT INTO {_COUNTER_TABLE} '
    '(scope, key, window_start, hit_count, expires_at) '
    'VALUES (?, ?, ?, 1, ?) '
    'ON CONFLICT(scope, key, window_start) DO UPDATE SET '
    'hit_count = hit_count + 1 '
    'RETURNING hit_count'
)


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


def normalize_username_key(username: str) -> str:
    """Return the lowercase username used as a login-failure key.

    Args:
        username: Raw username from the request body.

    Returns:
        Strip + lowercase form so ``Alice`` and ``alice`` share a bucket.
    """
    return username.strip().lower()


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
        scope: Bucket family (``auth_ip`` or ``login_user``).
        key: Client IP key or normalized username.
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


def peek_counter(
    scope: str,
    key: str,
    window_seconds: int,
    *,
    now: float | None = None,
    engine: Engine | None = None,
) -> int:
    """Return the current window count without incrementing.

    Args:
        scope: Bucket family.
        key: Client IP key or normalized username.
        window_seconds: Fixed-window length.
        now: Unix timestamp override for tests.
        engine: Optional SQLAlchemy engine.

    Returns:
        Stored hits, or ``0`` when missing or the read fails (fail-open).
    """
    clock = time.time() if now is None else now
    params = {
        'scope': scope,
        'key': key,
        'window_start': _window_start(clock, window_seconds),
        'now': int(clock),
    }
    bind = engine if engine is not None else db.engine
    try:
        with bind.connect() as conn:
            value = conn.execute(text(_PEEK_SQL), params).scalar()
        return int(value) if value is not None else 0
    except Exception as exc:
        _log_store_failure(exc)
        return 0


def reset_counter(
    scope: str,
    key: str,
    *,
    engine: Engine | None = None,
) -> None:
    """Delete every window for ``(scope, key)``.

    Args:
        scope: Bucket family.
        key: Client IP key or normalized username.
        engine: Optional SQLAlchemy engine.

    Fail-open: a delete error is logged and swallowed.
    """
    bind = engine if engine is not None else db.engine
    try:
        with bind.connect() as conn:
            conn.execute(text(_RESET_SQL), {'scope': scope, 'key': key})
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
        try:
            count = increment_counter(AUTH_IP_SCOPE, key, window)
        except Exception as exc:
            _log_store_failure(exc)
            return func(*args, **kwargs)
        if count is None:
            return func(*args, **kwargs)
        if count > max_hits:
            return _limit_response(_retry_after(window))
        return func(*args, **kwargs)

    return decorated


def username_login_blocked(username: str) -> tuple[Response, int] | None:
    """Return a 429 if this username is over the failed-login limit.

    Peek only — the password is not checked and the counter is not
    incremented. Missing and existing usernames share this path.

    Args:
        username: Raw username from the request body.

    Returns:
        The JSON 429 tuple, or ``None`` when the attempt may proceed.
    """
    if not current_app.config.get('RATELIMIT_ENABLED', True):
        return None
    max_hits = int(current_app.config.get('RATELIMIT_LOGIN_USER_MAX', 5))
    window = int(current_app.config.get('RATELIMIT_LOGIN_USER_WINDOW_SECONDS', 900))
    key = normalize_username_key(username)
    try:
        count = peek_counter(LOGIN_USER_SCOPE, key, window)
    except Exception as exc:
        _log_store_failure(exc)
        return None
    if count >= max_hits:
        return _limit_response(_retry_after(window))
    return None


def record_failed_login(username: str) -> None:
    """Count a failed password login against the normalized username.

    Args:
        username: Raw username from the request body.
    """
    if not current_app.config.get('RATELIMIT_ENABLED', True):
        return
    window = int(current_app.config.get('RATELIMIT_LOGIN_USER_WINDOW_SECONDS', 900))
    increment_counter(LOGIN_USER_SCOPE, normalize_username_key(username), window)


def reset_failed_logins(username: str) -> None:
    """Clear failed-login counters after a successful password login.

    Args:
        username: Raw username from the request body.
    """
    if not current_app.config.get('RATELIMIT_ENABLED', True):
        return
    reset_counter(LOGIN_USER_SCOPE, normalize_username_key(username))


def _window_start(now: float, window_seconds: int) -> int:
    now_i = int(now)
    return now_i - (now_i % window_seconds)


def _retry_after(window_seconds: int, now: float | None = None) -> int:
    clock = time.time() if now is None else now
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
    message = 'Rate limit store failed open: %s'
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
    clock = time.time() if now is None else now
    window_start = _window_start(clock, window_seconds)
    params = {
        'scope': scope,
        'key': key,
        'window_start': window_start,
        'expires_at': window_start + window_seconds,
        'now': int(clock),
    }
    bind = engine if engine is not None else db.engine
    if bind.dialect.name == 'sqlite':
        return _atomic_hit_sqlite(bind, params)
    return _atomic_hit_sql(bind, params)


def _atomic_hit_sqlite(engine: Engine, params: Mapping[str, Any]) -> int:
    raw = engine.raw_connection()
    old_iso = getattr(raw, 'isolation_level', None)
    try:
        setattr(raw, 'isolation_level', None)
        cursor = raw.cursor()
        try:
            cursor.execute('BEGIN IMMEDIATE')
            cursor.execute(
                _SQLITE_UPSERT,
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


def _atomic_hit_sql(engine: Engine, params: Mapping[str, Any]) -> int:
    with engine.connect() as conn:
        count = int(conn.execute(text(_UPSERT_SQL), dict(params)).scalar_one())
        if _should_prune(count, int(params['now'])):
            conn.execute(text(_PRUNE_SQL), {'now': params['now']})
        conn.commit()
        return count
