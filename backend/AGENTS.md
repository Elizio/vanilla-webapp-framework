# Backend Agent Guide

Flask REST API with JWT auth, custom SQLAlchemy layer, and Flasgger Swagger. Global context: [../AGENTS.md](../AGENTS.md). Standards: [../.cursor/rules/backend-rules.mdc](../.cursor/rules/backend-rules.mdc).

## Directory map

```
backend/
├── __init__.py          # create_app() factory, blueprint registration, init_db()
├── app.py               # Dev entrypoint
├── web_routes.py        # SPA fallback + error handlers
├── alembic.ini          # Alembic config
├── api/
│   ├── auth.py          # auth_bp — login, register, @token_required
│   ├── billing.py       # billing_bp — plans, checkout, webhooks
│   └── routes.py        # api_bp — public and protected endpoints
├── billing/             # Provider-agnostic billing (see Billing section)
│   ├── plans.py         # Plan catalog (outcome: entitlement / credits / none)
│   ├── service.py       # Checkout + webhook orchestration
│   ├── entitlements.py  # Feature gates, @entitlement_required
│   ├── credits.py       # Credit ledger helpers
│   └── providers/       # One adapter per payment provider
├── models/              # Data-only SQLAlchemy models
├── db_repository/
│   ├── database.py      # Engine, session, Base singleton
│   └── migrations/      # Alembic migrations
├── config/
│   ├── app_config.py    # AppConfig singleton (.env, APP_PROFILE)
│   ├── user_config.py   # PROJECT_FOLDER, log paths
│   └── logging_config.py
└── tests/               # pytest integration tests
```

## App initialization

`create_app()` in `backend/__init__.py`:

1. Creates Flask app with CORS
2. Loads `AppConfig.get_instance()` into `app.config`
3. Merges `UserConfig` values
4. Calls `setup_logging(app)`
5. Initializes Flasgger Swagger (`/docs`)
6. Registers `auth_bp`, `api_bp`, `oauth_bp`, and `billing_bp`
7. Registers web routes via `register_web_routes(app)`
8. Runs `init_db()` (dev/test) or `run_migrations()` (production)

A module-level `app = create_app()` runs at import time. Tests call `create_app()` again via fixtures in `tests/conftest.py`.

Error handlers and SPA fallback live in `web_routes.py`, registered from the factory.

**Canonical references:** `@backend/__init__.py`, `@backend/app.py`

## Blueprints

| Blueprint | File | Routes |
|-----------|------|--------|
| `auth_bp` | `api/auth.py` | `POST /api/login`, `POST /api/register` |
| `oauth_bp` | `api/oauth.py` | `GET /api/auth/<provider>/login`, `GET /api/auth/<provider>/callback`, `GET /api/auth/providers` |
| `billing_bp` | `api/billing.py` | `GET /api/billing/plans`, `GET /api/billing/status`, `POST /api/billing/checkout`, `POST /api/billing/webhook/lemon-squeezy` |
| `api_bp` | `api/routes.py` | `GET /api/health`, `GET /api/public`, `GET /api/data` (protected), `GET /api/supporter-badge` (entitlement-gated demo) |

Register new blueprints in `create_app()`:

```python
from .api.myfeature import myfeature_bp
app.register_blueprint(myfeature_bp)
```

Keep route handlers in blueprints — not in `app.py` (except `/` and error handlers).

## Recipe: add an API endpoint

1. **Create or extend a blueprint** in `backend/api/`

```python
from flask import Blueprint, jsonify
from .auth import token_required

myfeature_bp = Blueprint('myfeature', __name__)

@myfeature_bp.route('/api/myfeature', methods=['GET'])
@token_required
def get_myfeature(current_user):
    """
    Get myfeature data
    ---
    tags:
      - MyFeature
    security:
      - Bearer: []
    responses:
      200:
        description: Success
    """
    return jsonify({'user': current_user.username})
```

2. **Register** the blueprint in `backend/__init__.py` → `create_app()`
3. **Add a test** in `backend/tests/test_myfeature.py`
4. **Verify** at `http://localhost:5000/docs`

Copy Swagger docstring format from `@backend/api/routes.py` or `@backend/api/auth.py`.

## Billing — add a payment provider

Billing is **provider-agnostic**: plans, entitlements, credits, the SPA billing page, and feature gates live in the app. Each payment processor is a thin **adapter** that creates hosted checkout URLs and normalizes webhooks into `BillingWebhookResult`.

**Canonical references:** `@backend/billing/providers/base.py` (contract), `@backend/billing/providers/lemon_squeezy.py` (working adapter), `@backend/billing/providers/stripe.py` (stub + step-by-step template), `@backend/billing/service.py`, `@backend/billing/plans.py`, `@backend/api/billing.py`, `@backend/tests/test_billing.py`

### Layering

| Layer | Role | Provider-specific? |
|-------|------|--------------------|
| `billing/plans.py` | Plan catalog (`outcome`: `entitlement`, `credits`, or `none`) | No — provider ids come from env vars referenced in each plan |
| `billing/providers/*.py` | Checkout creation, webhook verify + parse | Yes — one class per provider |
| `billing/service.py` | Validate checkout, apply parsed webhook to DB (idempotent) | No |
| `billing/entitlements.py` / `credits.py` | App-owned access state | No |
| `models/billing_*` | Entitlements, webhook audit log, credit ledger | No |
| `api/billing.py` | HTTP routes; frontend talks only here | Webhook route per provider |

Checkout uses a **single active provider** selected by `BILLING_PROVIDER` (default `lemon_squeezy`). Entitlements are keyed by `(user_id, plan_key, provider)` so the same user can hold parallel grants during a provider migration.

### Recipe: new provider adapter

1. **Create** `backend/billing/providers/<provider>.py` implementing `BillingProvider` (`@backend/billing/providers/base.py`):

   | Method | Responsibility |
   |--------|----------------|
   | `name` | Stable key (e.g. `mercado_pago`) |
   | `is_configured()` | True when required env vars are set |
   | `create_checkout(...)` | Return hosted checkout URL; embed `user.id` in provider metadata/custom fields so webhooks can resolve the user |
   | `verify_webhook(raw_body, headers)` | Validate signature; raise `WebhookVerificationError` on failure |
   | `parse_webhook(raw_body, headers)` | Return `BillingWebhookResult` with stable `event_id` for idempotency |

   Copy structure from `@backend/billing/providers/lemon_squeezy.py`. Use `@backend/billing/providers/stripe.py` module docstring for a second worked outline (Stripe Checkout Session events).

2. **Register** the class in `backend/billing/providers/__init__.py` → `_PROVIDERS` dict.

3. **Wire plans** in `backend/billing/plans.py` — under each plan's `providers` map, add an entry pointing to env var **names** (never hardcode ids):

   ```python
   'providers': {
       'lemon_squeezy': {'variant_env': 'LEMON_SQUEEZY_VARIANT_ID_SUPPORTER'},
       'mercado_pago': {'price_env': 'MERCADO_PAGO_PRICE_ID_SUPPORTER'},  # example
   },
   ```

4. **Configuration** — add provider env vars to `AppConfig` (`backend/config/app_config.py`), `.env.example`, and [docs/billing-configuration.md](../docs/billing-configuration.md) (human dashboard setup for that provider). README env table only — no console steps in README or AGENTS.

5. **Webhook route** in `backend/api/billing.py`:

   ```python
   @billing_bp.route('/api/billing/webhook/<provider-key>', methods=['POST'])
   def provider_webhook():
       # raw_body = request.get_data(); service.handle_webhook(...)
   ```

   Today `service.handle_webhook` uses `get_billing_provider()` from `BILLING_PROVIDER`. For a **second concurrent provider** (e.g. global card + Brazil PIX), extend `handle_webhook` to accept an optional provider key before adding the route.

6. **Tests** in `backend/tests/test_billing.py` (or `test_<provider>_billing.py`) — mock the provider HTTP API for checkout; construct signed webhook payloads; assert entitlements/credits and idempotency. See existing Lemon Squeezy tests.

7. **Verify** — `pytest`; optional manual test with provider sandbox + webhook tunnel (ngrok/cloudflared).

### Webhook → domain mapping

`parse_webhook` must populate `BillingWebhookResult` so `service._apply_result` can branch on `plan.outcome`:

| Plan `outcome` | Set on result | Service action |
|----------------|---------------|----------------|
| `entitlement` | `entitlement_status` (`active` / `canceled` / `expired` / `past_due`), `provider_reference_id`, optional `current_period_end` | `upsert_entitlement()` |
| `credits` | `amount_cents`, `provider_reference_id` | `add_credits()` (guarded by provider order id) |
| `none` | `handled=False` or omit grant fields | Audit log only |

Always set a **stable** `event_id` (e.g. `{event_type}:{provider_object_id}:{updated_at}`) — duplicates are ignored via `billing_events`.

### Feature gating (unchanged when swapping providers)

```python
from backend.billing.entitlements import entitlement_required, user_has_plan

@api_bp.route('/api/my-feature')
@token_required
@entitlement_required('supporter')
def my_feature(current_user):
    ...
```

Spend in-app budget with `billing.credits.spend_credits()` in fork feature code.

### Do not change when adding a provider

- Entitlement/credit tables and helpers
- Frontend billing page (`frontend/src/js/controllers/billing.js`) — it only calls `/api/billing/*`
- Plan `outcome` semantics

Human provider setup (dashboard, webhooks, test mode) → [docs/billing-configuration.md](../docs/billing-configuration.md).

## JWT authentication

Flow:

1. `POST /api/register` — creates user, sets httpOnly session cookie
2. `POST /api/login` — sets httpOnly `auth_token` cookie (JWT inside)
3. `GET /api/auth/<provider>/login` — OAuth redirect; callback sets cookie
4. `GET /api/auth/session` — SPA bootstrap (authenticated + username)
5. `POST /api/logout` — clears cookie (CSRF-protected)
6. Protected routes use `@token_required` — reads cookie or `Authorization: Bearer`

CSRF: `GET /api/csrf` then send `X-CSRF-Token` header on mutating routes.

**Canonical reference:** `@backend/api/auth.py`, `@backend/api/session_auth.py`, `@backend/api/csrf.py`

### Config note

New code should read settings from `AppConfig.get_instance()` or `current_app.config`. Call `load_env_file()` only if you must read env before Flask starts (see `database.py`).

## Database layer

This project uses a **custom SQLAlchemy singleton**, not Flask-SQLAlchemy.

```python
from backend.db_repository.database import db, db_session, init_db
from backend.models.user import User
```

| Pattern | Usage |
|---------|--------|
| Model base | `class MyModel(db.Base)` |
| Query (legacy style) | `User.query.filter_by(username=x).first()` |
| Session writes | `db_session.add(obj)` → `db_session.commit()` |
| Session reads (2.0 style) | `db_session.get(User, id)` |
| Init tables | `init_db()` in factory |
| Testing | `APP_PROFILE=testing` → in-memory SQLite |

**Transaction pattern for new code:**

```python
try:
    db_session.add(user)
    db_session.commit()
except Exception:
    db_session.rollback()
    raise
```

No manual schema coordination in dev/test — use Alembic for production (see Alembic section).

**Canonical references:** `@backend/db_repository/database.py`, `@backend/models/user.py`

## Models

- Define in `backend/models/`
- Extend `db.Base`, set `__tablename__`
- Keep data-only — no business logic in models
- Export from `backend/models/__init__.py`

## Configuration

`AppConfig` singleton ([`backend/config/app_config.py`](backend/config/app_config.py)):

- **`load_env_file()`** — loads `<repo>/.env` once via python-dotenv (`override=False`); skipped when `APP_PROFILE=production`
- Optional override path: set `ENV_FILE` before starting the app
- **`AppConfig.get_instance()`** — reads validated settings from `os.environ` after the file load
- Required in non-testing: `FLASK_SECRET`, `JWT_SECRET`, `DATABASE_URI`

`UserConfig` provides `PROJECT_FOLDER` for log file paths (also uses `load_env_file()`).

`database.py` reads the database URI from `AppConfig`, not raw `os.environ`.

Logging writes to `{PROJECT_FOLDER}/logs/app.log` via `setup_logging(app)`.

## Error handling

- **Blueprint handlers** — return `jsonify({...}), status_code` directly
- **Global handlers** — `@app.errorhandler` in `app.py` returns JSON for 404/500
- **Logging** — use `app.logger.error(...)` in handlers

## Testing

Run from project root:

```bash
pytest
```

Fixtures in `tests/conftest.py`:

| Fixture | Purpose |
|---------|---------|
| `set_test_env` | Sets `APP_PROFILE=testing` (session-scoped) |
| `test_app` | Fresh `create_app()` with `TESTING=True` |
| `test_client` | Flask test client |
| `test_db` | Clean schema per test (`drop_all` → `init_db`; engine not disposed) |

**Test pattern:**

```python
def test_my_endpoint(test_client, test_db):
    response = test_client.get('/api/public')
    assert response.status_code == 200
```

For auth tests, register a user first, login for token, then call protected routes with `Authorization: Bearer <token>` header. See `@backend/tests/test_auth.py`.

Coverage is configured in `setup.cfg` (`--cov=backend`).

## Swagger

- UI: `/docs`
- Spec: `/apispec.json`
- Every endpoint needs a Flasgger YAML docstring (`---` block)
- Protected routes include `security: [{ Bearer: [] }]`

## Alembic migrations

- Config: `backend/alembic.ini`
- Scripts: `backend/db_repository/migrations/`
- Dev/test: `init_db()` via `create_all()`
- Production: `alembic upgrade head` via `run_migrations()` in `create_app()`

```bash
# From project root with DATABASE_URI set
alembic -c backend/alembic.ini upgrade head
alembic -c backend/alembic.ini revision --autogenerate -m "describe change"
```

## Notes

- Session teardown: `db._Session.remove()` on `teardown_appcontext`
- JWT config read from `current_app.config` in request handlers
- `register()` wraps commits with rollback on error

## Code documentation

Enforceable rules: [../.cursor/rules/documentation.mdc](../.cursor/rules/documentation.mdc). API routes also require Swagger (see Swagger section below).

### Module docstring

```python
"""OAuth 2.0 social login via Authlib (Google, Facebook)."""
```

### Public function (Google-style + type hints)

```python
from backend.models.user import User

def find_or_create_oauth_user(provider: str, subject: str, email: str | None) -> User:
    """Find an existing OAuth user or create a new OAuth-only account.

    Args:
        provider: OAuth provider key (e.g. ``google``).
        subject: Provider-specific user id.
        email: Email from provider profile, if available.

    Returns:
        The matched or newly created User.

    Raises:
        SQLAlchemyError: On database commit failure.
    """
```

### API route handler

Use the Flasgger YAML block only — no separate docstring duplicating Swagger:

```python
@api_bp.route('/api/public', methods=['GET'])
def public_data():
    """
    Get public data
    ---
    tags:
      - Public
    responses:
      200:
        description: Success
    """
    return jsonify({'message': 'Public data'})
```

**Canonical references:** `@backend/api/oauth.py`, `@backend/api/routes.py`

## See also

- [../AGENTS.md](../AGENTS.md) — global setup and verification
- [../frontend/AGENTS.md](../frontend/AGENTS.md) — SPA integration
- [../.cursor/rules/backend-rules.mdc](../.cursor/rules/backend-rules.mdc) — coding standards
