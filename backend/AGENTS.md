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
│   └── routes.py        # api_bp — public and protected endpoints
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
6. Registers `auth_bp` and `api_bp`
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
| `api_bp` | `api/routes.py` | `GET /api/health`, `GET /api/public`, `GET /api/data` (protected) |

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

## JWT authentication

Flow:

1. `POST /api/register` — creates user with werkzeug password hash
2. `POST /api/login` — returns `{ "token": "<jwt>" }` (HS256, 1h expiry)
3. `GET /api/auth/<provider>/login` — OAuth redirect (Google, Facebook); callback issues JWT via URL fragment
4. Protected routes use `@token_required` — reads `Authorization: Bearer <token>`

The decorator injects `current_user` as the first argument:

```python
@api_bp.route('/api/data', methods=['GET'])
@token_required
def protected_data(current_user):
    return jsonify({'message': 'Secure data'})
```

**Canonical reference:** `@backend/api/auth.py`

### Config note

`auth.py` and `database.py` read `os.environ` directly. New code should prefer `AppConfig` / `current_app.config` to avoid config drift.

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

No migrations yet — schema changes require coordinating `create_all()` across environments.

**Canonical references:** `@backend/db_repository/database.py`, `@backend/models/user.py`

## Models

- Define in `backend/models/`
- Extend `db.Base`, set `__tablename__`
- Keep data-only — no business logic in models
- Export from `backend/models/__init__.py`

## Configuration

`AppConfig` singleton (`backend/config/app_config.py`):

- Loads `.env` via python-dotenv
- `APP_PROFILE` drives `DEBUG`, `TESTING`, and test DB fallback
- Required in non-testing: `FLASK_SECRET`, `JWT_SECRET`, `DATABASE_URI`

`UserConfig` provides `PROJECT_FOLDER` for log file paths.

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
| `test_db` | Calls `db.init_db()`, tears down with `db.close()` |

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
