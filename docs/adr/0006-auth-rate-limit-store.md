# ADR 0006: Shared-database auth rate limits

## Status

Accepted

## Context

Login and register were limited in a per-process dict keyed only on `request.remote_addr`, skipped entirely when `TESTING` was true, and never pruned. Production runs `gunicorn --workers 2` against SQLite at `/data/app.db`. A rotating client IPv4 pool therefore never hit 429. Adding Redis would be a new service; the app already has a database.

## Decision

- Store counters in `rate_limit_counters` (Alembic 007) keyed by `(scope, key, window_start)`. `key` is `sha256(logical_key).hexdigest()`, not the raw IP or username.
- One atomic upsert per hit (`INSERT ... ON CONFLICT DO UPDATE ... RETURNING`). SQLite uses `BEGIN IMMEDIATE` and a short `busy_timeout` (~3 s on the limiter connection) so two workers cannot lose counts.
- Limits are **fixed-window and approximate** (a burst across a window edge can admit up to ~2× the cap): 10 auth requests / 60 s per client IP (IPv6 grouped by /64); 5 login attempts / 15 min per **exact** stripped username (not lowercased). The username counter increments before the password check. Success resets only that exact username key. Exceeded → 429 `RATE_LIMIT_EXCEEDED` + `Retry-After`.
- `RATELIMIT_ENABLED` defaults on in production and development, off in testing. Tests that assert 429 turn it on.
- Store errors fail open and log a warning (`Rate limit store failed open`).
- `TRUST_PROXY_HOPS` (default 1) is the ProxyFix `x_for` hop count and **must equal the number of trusted proxies**. Appending the connecting client to `X-Forwarded-For` is fine with `x_for=1`.

## Consequences

- Deploy runs 007 once in `docker-entrypoint.sh` (additive empty table). No WAL journal-mode change.
- Username lockout works across IP pools and does not cross case variants. A store outage does not block login.
- No Redis or extra process. Postgres uses the same upsert SQL.
- Image-only rollback leaves an unused empty table; downgrade drops it.
