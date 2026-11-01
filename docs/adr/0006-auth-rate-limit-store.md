# ADR 0006: Shared-database auth rate limits

## Status

Accepted

## Context

Login and register were limited in a per-process dict keyed only on `request.remote_addr`, skipped entirely when `TESTING` was true, and never pruned. Production runs `gunicorn --workers 2` against SQLite at `/data/app.db`. A rotating client IPv4 pool therefore never hit 429. Adding Redis would be a new service; the app already has a database.

## Decision

- Store counters in `rate_limit_counters` (Alembic 007) keyed by `(scope, key, window_start)`.
- One atomic upsert per hit (`INSERT ... ON CONFLICT DO UPDATE ... RETURNING`). SQLite uses `BEGIN IMMEDIATE`, `busy_timeout`, and WAL so two workers cannot lose counts.
- Limits: 10 auth requests / 60 s per client IP (IPv6 grouped by /64); 5 failed logins / 15 min per lowercase username. Success resets the username row. Exceeded → 429 `RATE_LIMIT_EXCEEDED` + `Retry-After`.
- `RATELIMIT_ENABLED` defaults on in production and development, off in testing. Tests that assert 429 turn it on.
- Store errors fail open and log a warning.
- `TRUST_PROXY_HOPS` (default 1) is the ProxyFix `x_for` hop count. Caddy must not trust client-sent `X-Forwarded-For`.

## Consequences

- Deploy runs 007 once in `docker-entrypoint.sh` (additive empty table). SQLite grows `-wal`/`-shm` files beside `/data/app.db`.
- Username lockout works across IP pools. A store outage does not block login.
- No Redis or extra process. Postgres uses the same upsert SQL.
- Image-only rollback leaves an unused empty table; downgrade drops it.
