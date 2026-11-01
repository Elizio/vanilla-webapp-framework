"""Shared-database rate limiting for login and register."""

from __future__ import annotations

import hashlib
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
STORE_FAILED_OPEN = 'Rate limit store failed open'
SQLITE_BUSY_TIMEOUT_MS = 3000


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


def _now() -> float:
    """Return the current Unix time (tests replace this, not ``time.time``)."""
    return time.time()


def hashed_counter_key(key: str) -> str:
    """Return the SHA-256 hex digest stored in ``rate_limit_counters.key``.

    Args:
        key: Logical key (client IP grouping or exact stripped username).

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


def username_key(username: str) -> str:
    """Return the exact stripped username used for login lookup.

    Args:
        username: Raw username from the request body.

    Returns:
        ``username.strip()`` — not lowercased, matching ``User.username``.
    """
    return username.strip()


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
        key: Logical client IP key or exact username.
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
        key: Logical client IP key or exact username.
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
    """Increment the username counter; return 429 when the limit is exceeded.

    The increment happens before the password check so concurrent
    attempts cannot all sneak through. A later successful login resets
    this exact username key.

    Args:
        username: Raw username from the request body.

    Returns:
        The JSON 429 tuple, or ``None`` when the attempt may proceed.
    """
    if not current_app.config.get('RATELIMIT_ENABLED', True):
        return None
    max_hits = int(current_app.config.get('RATELIMIT_LOGIN_USER_MAX', 5))
    window = int(current_app.config.get('RATELIMIT_LOGIN_USER_WINDOW_SECONDS', 900))
    count = increment_counter(LOGIN_USER_SCOPE, username_key(username), window)
    if count is None:
        return None
    if count > max_hits:
        return _limit_response(_retry_after(window))
    return None


def reset_failed_logins(username: str) -> None:
    """Clear failed-login counters for this exact username after success.

    Args:
        username: Raw username from the request body (same string as lookup).
    """
    if not current_app.config.get('RATELIMIT_ENABLED', True):
        return
    reset_counter(LOGIN_USER_SCOPE, username_key(username))


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


def _atomic_hit_sql(engine: Engine, params: Mapping[str, Any]) -> int:
    with engine.connect() as conn:
        count = int(conn.execute(text(_UPSERT_NAMED), dict(params)).scalar_one())
        if _should_prune(count, int(params['now'])):
            conn.execute(text(_PRUNE_SQL), {'now': params['now']})
        conn.commit()
        return count
