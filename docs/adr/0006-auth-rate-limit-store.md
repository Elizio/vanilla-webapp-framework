# ADR 0006: Shared-database auth rate limits

## Status

Accepted

## Context

Login and register were limited in a per-process dict keyed only on `request.remote_addr`, skipped entirely when `TESTING` was true, and never pruned. Production runs `gunicorn --workers 2` against SQLite at `/data/app.db`. A rotating client IPv4 pool therefore never hit 429. Adding Redis would be a new service; the app already has a database.

## Decision

- Store counters in `rate_limit_counters` (Alembic 007) keyed by `(scope, key, window_start)`. `key` is `sha256(logical_key).hexdigest()`, not the raw IP or username.
- One atomic upsert per hit (`INSERT ... ON CONFLICT DO UPDATE ... RETURNING`). SQLite uses `BEGIN IMMEDIATE` and a short `busy_timeout` (~3 s on the limiter connection) so two workers cannot lose counts.
- Limits are **fixed-window and approximate** (a burst across a window edge can admit up to ~2× the cap):
  - 10 auth requests / 60 s per client IP (IPv6 grouped by /64). Unchanged.
  - **Trusted device** (signed `auth_device` cookie, HMAC via `FLASK_SECRET`, bound to `sha256(exact username)`, HttpOnly / SameSite=Lax / Secure in production, 30-day TTL, same Path as auth cookies): 5 attempts / 15 min per `(username, device)`. Hard 429. Not subject to the global username backoff.
  - **Untrusted** clients: hard 5 / 15 min per `(exact username, client subnet)` (IPv4 /24, IPv6 /64).
  - **Untrusted global** per exact username: first 5 attempts in the window check the password immediately; further attempts require exponential backoff (`2, 4, 8, …` seconds, cap **180 s**). Too-soon probes 429 without consuming a slot. **Bound: 15 untrusted password checks per username per 900 s window** (5 free + 10 backoff-spaced). A window-edge burst can approach ~2×.
- Increment happens before the password check (atomic slot / pair / device increment) so concurrent requests cannot all sneak through. Success resets **only** this client's pair or device counter — never the global username counter (an attacker cannot clear it by logging into a case-variant account). Keys stay case-exact.
- Checking the password during lockout and letting a correct guess through is rejected: that would restore brute force.
- `RATELIMIT_ENABLED` defaults on in production and development, off in testing. Tests that assert 429 turn it on.
- Store errors fail open and log a warning (`Rate limit store failed open`).
- `TRUST_PROXY_HOPS` **defaults to 1** (prod: `TRUST_PROXY=1`, Caddy in front, ProxyFix `x_for=1`). No prod env change. It must equal the number of trusted proxies. Appending the connecting client to `X-Forwarded-For` is fine with `x_for=1`.

## Consequences

- Deploy runs 007 once in `docker-entrypoint.sh` (additive empty table). No WAL journal-mode change. No schema change for device/backoff (extra rows in the same table; keys still SHA-256 hex).
- A known username cannot be locked out indefinitely from every IP. An attacker can slow untrusted guesses (max `Retry-After` 180 s) and hard-lock one subnet or stolen device cookie. The real user with a device cookie still logs in from a clean IP.
- Trade-off: users without a device cookie (first login, new browser, cookie cleared) share the untrusted backoff. They are delayed, not locked out. Device cookies persist across logout so a returning browser stays trusted.
- Username counters do not cross case variants. A store outage does not block login.
- No Redis or extra process. Postgres uses the same upsert SQL.
- Image-only rollback leaves an unused empty table; downgrade drops it.
