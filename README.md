# Vanilla WebApp Framework

A modern, lightweight web application framework that combines Flask backend with a vanilla JavaScript frontend, leveraging Alpine.js and Tailwind CSS for enhanced functionality and styling.

## Using this template

1. Click **Use this template** on GitHub. Ticking **Template repository** is a repo setting (ask the owner after merge — it is not part of this PR).
2. Clone the new repo, then `make setup`.
3. `make init NAME=my-app` — rewrites every name in [docs/template-placeholders.md](docs/template-placeholders.md), resets dated `docs/superpowers/` plans, and runs `make check`.
4. Fill `YOUR_GHCR_OWNER`, Hostinger VM/project, and GitHub owner in the generated values and on the VPS.
5. Confirm a search for `vanilla-webapp-framework`, `dsfor.fun`, and `1136636` is empty.

The `template-init` GitHub Actions job exercises this on a throwaway copy. **Do not add it to required branch-protection checks.** Required names stay `backend`, `frontend`, and `build-and-push` (plus `lint`).

## 🚀 Features

### Backend
- **Flask-based RESTful API**
  - Modular routing with Blueprints
  - SQLAlchemy ORM for database operations
  - JWT authentication for secure endpoints
  - Swagger documentation for API endpoints
  - Comprehensive error handling and logging

### Frontend
- **SPA-like Behavior**
  - Dynamic data loading with Fetch API
  - Alpine.js HTML fragments (`.hbs` files imported with Vite `?raw`; not Handlebars-rendered)
  - Alpine.js for lightweight state management
  - Tailwind CSS for utility-first styling
  - Responsive design support
  - Public welcome page for unauthenticated visitors (carousel, affiliate picks, ad slots)
  - Per-fork SEO toolbox (`SEO_MODE`, page metadata, `robots.txt`)

### Development & DevOps
- **Modern Development Workflow**
  - Vite for build optimization
  - Docker multi-stage image (non-root UID/GID 10001, migrate-once entrypoint, `HEALTHCHECK`)
  - GitHub Actions CI (`backend`, `frontend`, `lint`) plus GHCR publish
  - Automated testing with pytest and Vitest
  - Auto-deploy to the Hostinger VPS on every merge to `master`

## 🛠️ Tech Stack

### Backend
- Flask
- SQLAlchemy
- JWT Authentication
- Flasgger (Swagger)
- Python 3.x

### Frontend
- Vanilla JavaScript (ES6+)
- Alpine.js
- Tailwind CSS
- Vite

### DevOps
- Docker
- GitHub Actions
- GitHub Container Registry (`ghcr.io/elizio/vanilla-webapp-framework`)
- Hostinger VPS (Caddy at `/vanilla-webapp-framework`)
- pytest

## 📁 Project Structure

```
vanilla-webapp-framework/
├── backend/
│   ├── api/                    # Flask blueprints
│   ├── config/                 # Application configuration
│   ├── models/                 # SQLAlchemy models
│   ├── db_repository/          # Database layer + Alembic migrations
│   ├── static/                 # Vite production build output
│   ├── tests/                  # Backend tests
│   ├── __init__.py             # create_app() factory
│   ├── app.py                  # Dev / gunicorn entrypoint
│   └── web_routes.py           # SPA fallback + error handlers
├── frontend/
│   ├── src/
│   │   ├── js/                 # Alpine controllers, router, page registry
│   │   ├── styles/             # Tailwind entry CSS
│   │   ├── templates/          # Alpine HTML partials (.hbs, imported ?raw)
│   │   └── index.html          # SPA shell
│   ├── tests/                  # Vitest tests
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── ARCHITECTURE.md             # Codemap, recipes, README sync triggers
├── CONTRIBUTING.md             # PR/issue workflow
├── docs/                       # How-tos, ADRs, design specs
│   ├── adr/                    # Architecture decision records
│   ├── oauth-configuration.md  # OAuth setup (Google, Facebook)
│   ├── billing-configuration.md # Billing setup (Lemon Squeezy)
│   └── template-placeholders.md # Names rewritten by `make init`
├── .cursor/rules/              # Cursor coding standards
├── .env.example                # Environment variable template
├── Dockerfile
├── docker-entrypoint.sh        # validate env, migrate once, then gunicorn
├── scripts/
│   ├── check_pins.py           # CI pin verification
│   ├── deploy-hostinger.sh     # Hostinger VPS deploy (called from CI)
│   ├── install-lint-tools.sh   # pinned shellcheck, actionlint, gitleaks
│   ├── migrations-check.sh     # alembic upgrade/check/downgrade round-trip
│   └── smoke-image.sh          # container /api/health + / smoke (IMAGE=)
├── Makefile                    # setup, lint, format, test, check, migrate, migrations-check, smoke
├── pyproject.toml              # Ruff, mypy, coverage floor
├── .pre-commit-config.yaml     # Ruff, Biome, gitleaks, shellcheck, hygiene
├── requirements.txt
├── setup.py
└── AGENTS.md                   # Agent guide (AI contributors)
```

## 🚀 How-To Guides

Copy `.env.example` to `.env` and adjust values before running.

### Setup

1. **Install dependencies**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   make setup
   # same files CI uses: requirements-dev.txt, then pip install -e . --no-deps,
   # frontend npm ci, and pinned shellcheck/actionlint/gitleaks into .tools/
   ```

2. **Environment variables**

   Create `.env` in the project root (see `.env.example`):

   | Variable | Description |
   | --- | --- |
   | `FLASK_SECRET` | Secret key for Flask sessions and CSRF protection |
   | `JWT_SECRET` | Secret key for JWT token generation and validation |
   | `DATABASE_URI` | Database connection string (SQLite, PostgreSQL, MySQL, etc.) |
   | `APP_PROFILE` | `development`, `testing`, or `production` |
   | `FLASK_APP` | Flask CLI target (default `backend.app`). Required for `flask run` from the repo root. |
   | `PROJECT_FOLDER` | Used only when `LOG_TO_FILE=1` and `LOG_FILE` is unset: the directory that contains (or is) the log folder. Default `~/project_folder`. Not used for default stdout logging. |
   | `LOG_TO_FILE` / `LOG_FILE` | Opt-in file logging. `LOG_TO_FILE=1` (or `true`/`yes`) writes a rotating `app.log` under `PROJECT_FOLDER`. An explicit `LOG_FILE` path wins. Unset in the container (stdout). |
   | `PORT` | Container listen port (default `5000`). The image `HEALTHCHECK` uses the same value. |
   | `HEALTHCHECK_PATH` | Path the image `HEALTHCHECK` probes (default `/api/health`). |
   | `ENV_FILE` | Optional path to a dotenv file (default `<repo>/.env`). Ignored when `APP_PROFILE=production`. |
   | `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Google OAuth (optional) |
   | `FACEBOOK_CLIENT_ID` / `FACEBOOK_CLIENT_SECRET` | Facebook OAuth (optional) |
   | `FRONTEND_URL` | Full public app URL after OAuth/billing (keep any subpath; default `http://localhost:5173` in dev) |
   | `OAUTH_REDIRECT_BASE` | OAuth callback base URL (default `http://localhost:5173` in dev) |
   | `CORS_ORIGINS` | Comma-separated browser origins only (`scheme://host[:port]`, no paths). A path is stripped at startup with a warning. A malformed entry (no scheme/host) raises `ValueError` and stops startup. Defaults to the origin of `FRONTEND_URL`. |
   | `APP_BASE_PATH` | Public subpath prefix used as cookie `Path` for `auth_token`, `csrf_token`, `auth_device`, and the Flask session (default `/`). The `refresh_token` cookie is scoped to `{APP_BASE_PATH}/api/auth`. Use `/vanilla-webapp-framework` on the dsfor.fun subpath deploy. Empty/unset keeps access cookies at `Path=/`. |
   | `VITE_BASE_PATH` | Vite `base` at **image build time** (default `/`). Production CI sets `/vanilla-webapp-framework/`. Changing it requires a rebuild; it is not a runtime compose key. Must match `APP_BASE_PATH` plus a trailing slash. |
   | `TRUST_PROXY` | Set `1` behind Caddy/nginx so Flask honors `X-Forwarded-*` (default off). |
   | `TRUST_PROXY_HOPS` | How many `X-Forwarded-*` hops Flask peels when `TRUST_PROXY=1`. **Default `1`** (prod: `TRUST_PROXY=1`, Caddy, ProxyFix `x_for=1` — no prod env change). Must equal the number of trusted proxies. Appending the connecting client to `X-Forwarded-For` is fine with `x_for=1`. |
   | `RATELIMIT_ENABLED` | Auth rate limiter on/off. Default on in production and development, off in the testing profile. |
   | `RATELIMIT_AUTH_IP_MAX` | Login + register requests per client IP (IPv6 grouped by /64) per window (default `10`). |
   | `RATELIMIT_AUTH_IP_WINDOW_SECONDS` | Per-IP window length (default `60`). |
   | `RATELIMIT_LOGIN_USER_MAX` | Hard limit per exact username+subnet (untrusted) or username+device (trusted), and free untrusted attempts before backoff (default `5`). |
   | `RATELIMIT_LOGIN_USER_WINDOW_SECONDS` | Per-username / pair / device window (default `900`). Success resets only that client's pair or device counter, not the global backoff. |
   | `ACCESS_TOKEN_TTL_SECONDS` | Access JWT lifetime (default `900`). Cookie `auth_token` uses the same Max-Age. |
   | `REFRESH_TOKEN_TTL_DAYS` | Refresh family absolute cap and remember-me cookie lifetime (default `30`). |
   | `REFRESH_SESSION_TTL_HOURS` | Server TTL for a refresh token when remember-me is off (default `24`). The cookie is a browser-session cookie. |
   | `HSTS_ENABLED` | Production HSTS on/off (default on). Sends `max-age=31536000` without `includeSubDomains`. Keep on for at least one max-age before setting `0`. |
   | `SEO_MODE` | `auth-first` (default, noindex app pages) or `public-first` (indexable by default); drives frontend meta tags and `/robots.txt`. The public welcome page always uses `index, follow` regardless of mode. |
   | `SWAGGER_ENABLED` | Force Swagger UI on or off. Default: on in development/testing, off in production unless set to `true`/`1`/`yes`. |
   | `BILLING_PROVIDER` | Active billing adapter (default `lemon_squeezy`) |
   | `LEMON_SQUEEZY_API_KEY` | Lemon Squeezy API key (billing disabled until set) |
   | `LEMON_SQUEEZY_STORE_ID` | Lemon Squeezy store id used for checkouts |
   | `LEMON_SQUEEZY_WEBHOOK_SECRET` | Secret used to verify webhook signatures |
   | `LEMON_SQUEEZY_VARIANT_ID_SUPPORTER` | Variant id for the demo `supporter` donation plan |

3. **Database**

   - **Development:** `bootstrap_dev_database()` creates or upgrades the schema when Flask starts (`APP_PROFILE=development`).
   - **Testing:** `APP_PROFILE=testing` uses in-memory SQLite (pytest fixtures). Schema changes still go through Alembic.
   - **Production:** the container entrypoint runs `alembic -c backend/alembic.ini upgrade head` once, then gunicorn. Local `flask run` does **not** migrate:

     ```bash
     make migrate
     # or: alembic -c backend/alembic.ini upgrade head
     ```

### Run — development

Use the Vite dev server in the browser (not Flask directly). Run both commands from the **repository root**:

```bash
# Terminal 1 — API on :5000
flask run

# Terminal 2 — SPA on :5173
cd frontend && npm run dev
```

`flask run` uses `FLASK_APP=backend.app` from `.env`. Open **http://localhost:5173**. Vite proxies `/api/*` to Flask on port 5000.

API-only work: `flask run` is enough. Swagger UI: http://localhost:5000/docs

### Run — production (local smoke test)

```bash
cd frontend && npm run build
make migrate   # or: alembic -c backend/alembic.ini upgrade head
APP_PROFILE=production flask run
```

`flask run` no longer runs migrations. The Docker image runs `alembic upgrade head` once in `docker-entrypoint.sh` before gunicorn.

Open **http://localhost:5000**. Flask serves the Vite build from `backend/static/`.

### Run — Docker

```bash
docker build -t vanilla-webapp .
docker run -p 5000:5000 \
  -e DATABASE_URI=postgresql://user:pass@host/db \
  -e FLASK_SECRET=your-secret \
  -e JWT_SECRET=your-jwt-secret \
  -e APP_PROFILE=production \
  vanilla-webapp
```

The image runs as UID/GID **10001**, keeps `/app` read-only for that user, validates `FLASK_SECRET` / `JWT_SECRET` / `DATABASE_URI`, runs `alembic -c backend/alembic.ini upgrade head` once, then gunicorn. Logs go to stdout. The image `HEALTHCHECK` probes `GET $HEALTHCHECK_PATH` (default `/api/health`).

**Existing named volumes:** chown the data directory on the host **before** upgrading to this image:

```bash
# On the VPS, as root, against the volume's mount (example path)
chown -R 10001:10001 /path/to/data
```

Do not chown at container start. The entrypoint runs as 10001 and cannot fix ownership.

### Run — testing

```bash
make check          # same gates as CI: pins, audit, lint, linter-fail proofs,
                    # alembic check, frontend build + backend/static/index.html, tests
# or separately:
make test           # pytest (coverage floor) + npm run test:coverage
make lint
make migrations-check
cd frontend && npm run build && npm run test:coverage
# Docker image smoke (CI build-and-push, before push): IMAGE=... make smoke
```

Coverage floors: backend `fail_under` in `pyproject.toml` (omits `backend/tests`); frontend thresholds in `frontend/vitest.config.js` over `src/js`. Raise a floor when coverage goes up by at least 1 point. Do not lower one without a PR justification. See [AGENTS.md](AGENTS.md) → Coverage ratchet.

### Configure & operate

- **OAuth / social login:** optional Google and Facebook. See [docs/oauth-configuration.md](docs/oauth-configuration.md) for provider console setup, redirect URIs, and troubleshooting. Env vars remain in the table above.
  - Inactive users get **403** `ACCOUNT_INACTIVE` on password login, session, and OAuth callback (not a silent 200).
  - Google links an existing password account by email **only** when `email_verified` is true.
  - Facebook never links by email (Graph `me` has no verified flag); it creates or reuses its own provider account.
  - `users.password_hash` is `String(255)` (Werkzeug scrypt hashes are ~162 characters).
- **Billing:** optional Lemon Squeezy demo (donations, spot purchases, credit top-ups). See [docs/billing-configuration.md](docs/billing-configuration.md) for dashboard setup, webhooks, test mode, and troubleshooting. Env vars remain in the table above.
- **Subpath cookies and HSTS:** behind a prefix-stripping proxy (Caddy), Flask still sees `/api/...`. Set `APP_BASE_PATH` to the public prefix (no trailing slash) so cookies are not host-wide. `CORS_ORIGINS` is origin-only (`scheme://host[:port]`); do not put a path there. `Path` is not a security boundary between same-origin apps — a sibling `Path=/` cookie is still sent here; a dedicated subdomain (for example `vwf.dsfor.fun`) is the real isolation. Production HSTS is `max-age=31536000` without `includeSubDomains` so a later header replaces a cached includeSubDomains policy (RFC 6797 §8.1). Keep HSTS on for at least one max-age before `HSTS_ENABLED=0`. Prefer domain-wide HSTS on the reverse proxy if this host is shared.
- **Auth rate limits:** login and register share a per-IP bucket (default 10 / 60 s; IPv6 /64). Successful login/register sets a signed **`auth_device`** cookie (HMAC with `FLASK_SECRET`, bound to the exact username, 30-day TTL, same Path/flags as `auth_token`). A valid device cookie is trusted: 5 / 15 min per `(username, device)` only. Untrusted clients get 5 / 15 min per `(exact username, IPv4 /24 or IPv6 /64)` plus a global per-username backoff (5 free password checks, then 2, 4, 8, … s, cap 180 s) so a known name cannot be locked out from every IP. **Bound: 15 untrusted password checks per username per 15 min window** (~2× at a window edge). Success resets only that client's pair/device counter, not the global one. Limits are **fixed-window and approximate**. Exceeded limits return **429** `RATE_LIMIT_EXCEEDED` with `Retry-After`. Counters live in `rate_limit_counters` (SHA-256 keys). A store error fails open and logs `Rate limit store failed open`. `TRUST_PROXY_HOPS` **defaults to 1** (prod-ready with Caddy). Appending the client to `X-Forwarded-For` is fine with `x_for=1`.
- **Logs:** stdout/stderr by default (`docker logs`). File logging is opt-in (`LOG_TO_FILE=1` or `LOG_FILE`). `PROJECT_FOLDER` is not a log destination unless file logging is enabled without `LOG_FILE`.
- **Migrations (local production / `flask run`):** `make migrate` or `alembic -c backend/alembic.ini upgrade head` (the container entrypoint does this once before gunicorn). Revision **008** adds `users.token_version` (default 0). Revision **009** adds `refresh_tokens` (rotating refresh families). Existing users are not logged out; in-flight access JWTs work until `exp`, then a new login issues a refresh cookie.
- **Health check:** `GET /api/health` runs `SELECT 1` through the app database session. Returns 200 `{"status":"ok","db":"ok","version":"<APP_VERSION>"}` when the database is reachable, or 503 `{"status":"error","db":"error","version":"..."}` when it is not. `version` is the image git SHA (`APP_VERSION` bake-time env), or `unknown` when unset. Production deploy (`scripts/deploy-hostinger.sh`) requires `version ==` the merge commit SHA and rolls back to the previous `VWF_IMAGE` on failure.
- **Production deploy:** every merge to `master` runs `.github/workflows/docker-publish.yml`: required CI (`backend`, `frontend`, `build-and-push`, plus `lint`), then a private GHCR image tagged `sha-<full-commit>` (and `latest`), then `scripts/deploy-hostinger.sh` against Hostinger VM `1136636` / Docker project `dsfor` at `https://dsfor.fun/vanilla-webapp-framework`. The only secret the script needs is `HOSTINGER_API_TOKEN`. Production config lives on the VPS — do not commit it.
- **Git workflow:** open PRs against `master`. Never push to `master` or any default branch, and never merge your own work unless asked. Branch protection requires the branch to be **up to date** with `master` and the required checks to be green. Merging triggers the auto-deploy above.
- **API docs:** Swagger UI at `/docs` in development; disabled in production unless `SWAGGER_ENABLED=true`.
- **Create a migration revision:**

  ```bash
  alembic -c backend/alembic.ini revision --autogenerate -m "describe change"
  ```

- **AI contributors:** see [AGENTS.md](AGENTS.md) for agent workflows and verification checklists.

## 📝 Development Guidelines

### Backend Development
- Use Flask Blueprints for modular routing
- Follow RESTful conventions
- Implement proper error handling
- Write comprehensive tests
- Document all API endpoints

### Frontend Development
- Use Fetch API for data operations
- Implement responsive design
- Keep Alpine.js logic simple
- Leverage Tailwind utility classes
- Optimize assets with Vite
- Register pages in `frontend/src/js/pages.js` (controller + `?raw` template import)

### Code Standards
- Follow PEP 8 for Python code
- Use ES6+ for JavaScript
- Keep functions modular
- Add proper documentation
- Avoid global variables

## 🔒 Security

- Session auth via a short-lived httpOnly `auth_token` JWT (`user_id`, `iat`, `exp`, `tv`) plus a rotating httpOnly `refresh_token` cookie (`Path={APP_BASE_PATH}/api/auth`, `SameSite=Strict`, `Secure` in production). `POST /api/auth/logout` revokes that refresh family. `POST /api/auth/logout-all` bumps `users.token_version` and revokes every family (copied access JWTs become 401). Deprecated `POST /api/logout` still clears cookies. Bearer is for access tokens only.
- CSRF double-submit protection on mutating API routes (`GET /api/csrf` JSON token + HttpOnly `csrf_token` cookie + `X-CSRF-Token` header)
- CORS restricted to configured origins (`scheme://host[:port]` only) with credentials support
- Production HSTS `max-age=31536000` without `includeSubDomains`
- Rate limiting on login and registration (fixed windows: 10 / 60 s per IP; trusted device 5 / 15 min; untrusted 5 / 15 min per username+subnet plus global backoff, **15 password checks / 15 min** per username; approximate — bursts up to ~2× across a window edge), shared in the app database
- Input validation and structured error codes (no raw stack traces to clients)
- Inactive accounts: **403** `ACCOUNT_INACTIVE` after a correct password or a valid session/OAuth identity
- Bearer token header still supported for API clients and tests

## 📦 Deployment

- Docker multi-stage build (see **Run — Docker** above). Runtime user **10001:10001**, read-only `/app`, migrate-once entrypoint, image `HEALTHCHECK`.
- GitHub Actions: `backend` (pins, pip-audit, ruff, mypy, `alembic check`, pytest with coverage `fail_under`), `frontend` (Biome, npm audit, build + `backend/static/index.html`, Vitest coverage thresholds), `lint` (shellcheck + actionlint + gitleaks on full git history). `build-and-push` smokes the exact image (`/api/health` status ok and `/` 200) before push; PRs build and smoke without publishing. Actions are SHA-pinned; Dependabot updates them weekly (Python/node Docker majors are ignored). Biome does not lint `.hbs` templates. No extra required check names — new steps run inside `backend`, `frontend`, `lint`, and `build-and-push`.
- Production auto-deploy is `scripts/deploy-hostinger.sh`, invoked by `.github/workflows/docker-publish.yml` after CI and the GHCR publish (private image `ghcr.io/elizio/vanilla-webapp-framework:sha-<full>`). See **Configure & operate**.

## 📚 Documentation

- **How-to guides:** this README (setup, run, configure); [OAuth configuration](docs/oauth-configuration.md) (Google, Facebook); [Billing configuration](docs/billing-configuration.md) (Lemon Squeezy)
- **API reference:** Swagger UI at `/docs` when the Flask server is running
- **In-code docs:** Python docstrings + type hints; JavaScript JSDoc (see [AGENTS.md](AGENTS.md) and `.cursor/rules/documentation.mdc`)
- **Architecture / ADRs:** [ARCHITECTURE.md](ARCHITECTURE.md), [docs/adr/](docs/adr/)
- **Agent workflows:** [AGENTS.md](AGENTS.md), [backend/AGENTS.md](backend/AGENTS.md), [frontend/AGENTS.md](frontend/AGENTS.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Short version: `make setup && make check`, one PR per change, never push to `master`.

## 📄 License

MIT — see `setup.py` classifiers.

---

Built with ❤️ using modern web technologies
