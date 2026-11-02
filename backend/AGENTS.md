# Backend Agent Guide

Flask REST API with JWT auth, custom SQLAlchemy layer, and Flasgger Swagger. Global: [../AGENTS.md](../AGENTS.md). Codemap and recipes: [../ARCHITECTURE.md](../ARCHITECTURE.md). Standards: [../.cursor/rules/backend-rules.mdc](../.cursor/rules/backend-rules.mdc).

## Directory map

```
backend/
├── __init__.py          # create_app() factory
├── app.py               # Dev entrypoint
├── web_routes.py        # SPA fallback + error handlers
├── alembic.ini
├── api/                 # auth, rate_limit, billing, oauth, routes
├── billing/             # plans, service, entitlements, providers/
├── models/              # data-only SQLAlchemy (users, billing, rate_limit_counters, refresh_tokens)
├── db_repository/       # engine/session + migrations/
├── config/              # AppConfig, UserConfig, logging
└── tests/
```

## App initialization

`create_app()` in `backend/__init__.py`: CORS → `AppConfig` → `UserConfig` → `setup_logging` → Flasgger → blueprints (`auth`, `api`, `oauth`, `billing`, `csrf`) → `register_web_routes` → `bootstrap_dev_database()` (development). Schema changes go through Alembic (`make migrate` / `alembic -c backend/alembic.ini upgrade head`). Production migrations run once in `docker-entrypoint.sh`, not in the factory.

A module-level `app = create_app()` runs at import time. Tests call `create_app()` via `tests/conftest.py`.

**Canonical:** `@backend/__init__.py`, `@backend/app.py`, `@backend/web_routes.py`

## Blueprints

| Blueprint | File | Routes |
|-----------|------|--------|
| `auth_bp` | `api/auth.py` | `POST /api/login`, `POST /api/register`, `GET /api/auth/session`, `POST /api/auth/refresh`, `POST /api/auth/logout`, `POST /api/auth/logout-all`, deprecated `POST /api/logout` |
| `oauth_bp` | `api/oauth.py` | `/api/auth/<provider>/login`, `/callback`, `/providers` |
| `billing_bp` | `api/billing.py` | plans, status, checkout, Lemon Squeezy webhook |
| `api_bp` | `api/routes.py` | `/api/health`, `/api/public`, `/api/data`, `/api/supporter-badge` |

Register new blueprints in `create_app()`. Keep `/` and `@app.errorhandler` in `web_routes.py`. Recipe: [ARCHITECTURE.md](../ARCHITECTURE.md#add-an-api-endpoint).

## Billing

Provider-agnostic layer. To add an adapter: [ARCHITECTURE.md](../ARCHITECTURE.md#add-a-payment-provider). Human dashboard setup: [docs/billing-configuration.md](../docs/billing-configuration.md). Contract: `@backend/billing/providers/base.py`. Working adapter: `@backend/billing/providers/lemon_squeezy.py`.

## Auth

Cookie session + CSRF. Access JWTs carry `user_id`, `iat`, `exp`, `tv` (`users.token_version`, Alembic 008), and `sid` (refresh-token `family_id`, Alembic 009). Default access TTL is 900 s (`ACCESS_TOKEN_TTL_SECONDS`). `token_required` and `GET /api/auth/session` reject a token whose `tv` does not match; a missing `tv` counts as `0` so the deploy does not log anyone out. A present `sid` must be a live (unrevoked) family for that user — one indexed lookup on `refresh_tokens.family_id`. Tokens minted before `sid` omit it and stay on the `tv` check. Rotating opaque refresh tokens live in `refresh_tokens`, hashed SHA-256, cookie `refresh_token` at `{APP_BASE_PATH}/api/auth`. `POST /api/auth/refresh` (`@csrf_protect`) rotates; reuse after a 30 s grace window revokes the family. `POST /api/auth/logout` revokes that family so this device's access JWTs fail on the next request; other devices keep working. Logout of a legacy no-`sid` access token bumps `token_version` so that JWT dies immediately (other in-flight pre-deploy tokens for that user die too). `POST /api/auth/logout-all` (`@token_required`) calls `bump_token_version()` and revokes every family. Deprecated `POST /api/logout` uses the same revoke path (the access cookie is sent; the refresh cookie is not). `auth_device` is left in place. There is no password-change route today; #59 should call `bump_token_version()` (and revoke families). Inactive users: **403** `ACCOUNT_INACTIVE` (login, session, OAuth, refresh). Google links by email only when `email_verified`; Facebook never links by email. `users.password_hash` is `String(255)`.

Login/register rate limits live in `rate_limit_counters` (Alembic 007), shared across gunicorn workers. Fixed windows (approximate; ~2× at a window edge): per-IP (10 / 60 s, IPv6 /64); trusted `auth_device` cookie (5 / 15 min per username+device); untrusted username+subnet plus global backoff (**15 password checks / 900 s**). Increment before the password check. Store keys are SHA-256 hex. `TRUST_PROXY_HOPS` defaults to 1. `RATELIMIT_ENABLED` defaults off only in the testing profile — tests that assert 429 must turn it on. Store errors fail open. See [ADR 0006](../docs/adr/0006-auth-rate-limit-store.md).

**Canonical:** `@backend/api/auth.py`, `@backend/api/refresh_tokens.py`, `@backend/api/rate_limit.py`, `@backend/api/oauth.py`, `@backend/api/session_auth.py`, `@backend/api/csrf.py`

Read settings from `AppConfig.get_instance()` or `current_app.config`. Call `load_env_file()` only before Flask starts (`database.py`).

## Database

Custom SQLAlchemy singleton — not Flask-SQLAlchemy.

```python
from backend.db_repository.database import db, db_session
```

| Pattern | Usage |
|---------|--------|
| Model base | `class MyModel(db.Base)` |
| Writes | `db_session.add(obj)` → `commit()` / `rollback()` |
| Reads (2.0) | `db_session.get(User, id)` |
| Testing | `APP_PROFILE=testing` → in-memory SQLite |

Models stay data-only in `backend/models/` and export from `backend/models/__init__.py`.

`UserConfig.PROJECT_FOLDER` is used only when file logging is opted in (`LOG_TO_FILE` / `LOG_FILE`). Default logging is stdout/stderr. `setup_logging(app)` is called once from the factory.

## Testing

```bash
make test-backend
make migrations-check   # alembic upgrade / check / downgrade / upgrade
# or: pytest
# full local CI loop: make check
```

Fixtures in `tests/conftest.py`: `test_app`, `test_client`, `test_db`. Register + login for auth tests (`@backend/tests/test_auth.py`). Coverage: `fail_under` in `pyproject.toml` (omits `backend/tests`). Operator schema: `make migrate` / `alembic -c backend/alembic.ini upgrade head`.

## Swagger and Alembic

- UI `/docs`, spec `/apispec.json`. Every route needs a Flasgger `---` block (no second docstring).
- Config: `backend/alembic.ini`. Scripts: `backend/db_repository/migrations/`.
- Production: `alembic upgrade head` once in `docker-entrypoint.sh`. Local production: `make migrate`.
- Rollback is image-only: a new migration must stay compatible with the previous image.

```bash
make migrate
alembic -c backend/alembic.ini revision --autogenerate -m "describe change"
```

## Code documentation

Module docstring on every `.py` you touch; Google-style + type hints on public functions; Flasgger only on routes. Examples: [../ARCHITECTURE.md](../ARCHITECTURE.md#documentation-policy), [../.cursor/rules/documentation.mdc](../.cursor/rules/documentation.mdc).

## See also

- [../AGENTS.md](../AGENTS.md) — setup and verification
- [../ARCHITECTURE.md](../ARCHITECTURE.md) — recipes
- [../frontend/AGENTS.md](../frontend/AGENTS.md) — SPA
- [../.cursor/rules/backend-rules.mdc](../.cursor/rules/backend-rules.mdc)
