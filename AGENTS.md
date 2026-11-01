# Agent Guide — Vanilla WebApp Framework

Flask REST API + vanilla JavaScript SPA (Alpine.js, Tailwind, Vite). Human onboarding lives in [README.md](README.md). Coding standards live in [.cursor/rules/](.cursor/rules/). This file covers what agents need to run, verify, and extend the project.

## Documentation map

| Doc | Scope |
|-----|-------|
| **This file** | Global setup, verification, full-stack checklist, debt summary |
| [docs/oauth-configuration.md](docs/oauth-configuration.md) | OAuth setup (human): Google, Facebook |
| [docs/billing-configuration.md](docs/billing-configuration.md) | Billing setup (human): Lemon Squeezy, webhooks |
| [backend/AGENTS.md](backend/AGENTS.md) | Flask, DB, JWT, pytest recipes; **billing — add a provider** (code) |
| [frontend/AGENTS.md](frontend/AGENTS.md) | Vite, Alpine, controllers, templates |
| [.cursor/rules/](.cursor/rules/) | Enforceable coding standards (do not duplicate here) |
| [.cursor/rules/documentation.mdc](.cursor/rules/documentation.mdc) | README how-to sync + in-code doc enforcement |

## Repository layout

```
vanilla-webapp-framework/
├── backend/           # Flask API (see backend/AGENTS.md)
├── frontend/          # Vite SPA (see frontend/AGENTS.md)
├── .cursor/rules/     # Cursor rules (.mdc)
├── .env               # Required secrets (not committed)
├── requirements.txt   # Python deps
├── setup.py           # pip install -e .
├── .github/workflows/ # CI (pytest + frontend build/test)
├── scripts/           # check_pins.py, deploy-hostinger.sh
└── Dockerfile         # Multi-stage production image
```

## Environment setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e . --no-deps
```

Create `.env` in the project root:

| Variable | Purpose |
|----------|---------|
| `FLASK_SECRET` | Flask sessions / CSRF |
| `JWT_SECRET` | JWT signing |
| `DATABASE_URI` | DB connection string |
| `APP_PROFILE` | `development`, `testing`, or `production` |
| `FLASK_APP` | Flask CLI target (`backend.app`) so `flask run` works from the repo root |
| `PROJECT_FOLDER` | Only used when `LOG_TO_FILE=1` and `LOG_FILE` is unset (stdout/stderr by default) |
| `FRONTEND_URL` | Full public app URL (keep any subpath; default `http://localhost:5173` in dev) |
| `CORS_ORIGINS` | Origin-only (`scheme://host[:port]`). Paths are stripped with a warning; a malformed entry stops startup |
| `APP_BASE_PATH` | Public subpath used as cookie `Path` (default `/`) |
| `VITE_BASE_PATH` | Vite `base` at image build time (not a runtime compose key) |
| `TRUST_PROXY` | `1` behind Caddy/nginx so Flask honors `X-Forwarded-*` |
| `HSTS_ENABLED` | Production HSTS on/off (default on; plain `max-age`, no `includeSubDomains`) |
| `SEO_MODE` | `auth-first` (default) or `public-first`; frontend meta defaults + `/robots.txt` |
| `BILLING_PROVIDER` | Active billing adapter (default `lemon_squeezy`; optional) |
| `LEMON_SQUEEZY_*` | Lemon Squeezy API key, store id, webhook secret, variant ids (optional) |

Full operator table: [README.md](README.md) → Environment variables. Do not invent keys that are not in `.env.example`.

Register each provider's redirect URI as `{OAUTH_REDIRECT_BASE}/api/auth/{provider}/callback` (e.g. `http://localhost:5173/api/auth/google/callback` in dev so the Vite proxy keeps the session cookie on one origin).

## Development workflow

Run **both** servers during frontend work:

```bash
# Terminal 1 — API on :5000
flask run

# Terminal 2 — SPA on :5173
cd frontend && npm install && npm run dev
```

**Use `http://localhost:5173` in the browser**, not `:5000`. Vite proxies `/api/*` to Flask.

API-only work (no UI): `flask run` is sufficient. Swagger UI: `http://localhost:5000/docs`.

## Verification checklist

Run before claiming work is done:

- [ ] `pytest` from project root (backend tests with coverage)
- [ ] `cd frontend && npm run build && npm run test`
- [ ] `cd frontend && npm run dev` — app loads at `:5173`
- [ ] Production smoke: `cd frontend && npm run build && make migrate && APP_PROFILE=production flask run` → `:5000` (`flask run` no longer migrates)
- [ ] New API endpoints have Swagger docstrings and pytest coverage
- [ ] README how-tos checked against diff triggers (setup, run per environment, configure/operate)
- [ ] `.env.example` updated if env vars changed
- [ ] New/modified modules have docstrings; public APIs documented per documentation.mdc

## Documentation policy

Human **how-to guides** live in [README.md](README.md). Agents keep them accurate — do not relocate how-to prose here.

### README how-to categories

| Category | Update when |
|----------|-------------|
| **Project setup** | Install steps, env vars, database init/migrations change |
| **Run by environment** | Dev, production, Docker, or test run commands change |
| **Configure & operate** | OAuth, **billing provider dashboards/webhooks**, logs, Swagger, Alembic, CI, or troubleshooting steps change |

### README sync triggers

| Trigger | README section |
|---------|----------------|
| New env var or config | Project setup → Environment Variables; update `.env.example` |
| Database or migration change | Project setup + Configure & operate (Alembic) |
| Setup / install command change | Project setup |
| Run / start command change | Run by environment |
| New `APP_PROFILE` behavior | Run by environment for that profile |
| User-facing feature or API | Features, Tech Stack |
| Project layout change | Project Structure |
| Deployment / CI change | Run by environment, Deployment |
| OAuth or auth flow change | Project setup (vars), **Configure & operate** (link to [docs/oauth-configuration.md](docs/oauth-configuration.md)) |
| Billing provider setup, webhook URL, or checkout flow change | **Configure & operate** (link to [docs/billing-configuration.md](docs/billing-configuration.md)); env table; `.env.example` |
| New billing provider adapter (code only) | [backend/AGENTS.md](backend/AGENTS.md) → Billing; optional stub section in billing-configuration.md when human setup exists |
| Capability added or removed | Features (remove unimplemented claims) |

**When NOT to update README:** pure refactors, internal-only changes, test-only edits, agent recipes that belong in AGENTS only.

### In-code documentation

| Layer | Standard |
|-------|----------|
| Python | Module docstring; Google-style + type hints on public APIs; Flasgger Swagger on routes |
| JavaScript | File-level JSDoc; `@param` / `@returns` on exports when needed |

Details and examples: [backend/AGENTS.md](backend/AGENTS.md), [frontend/AGENTS.md](frontend/AGENTS.md). Enforceable rules: [.cursor/rules/documentation.mdc](.cursor/rules/documentation.mdc).

**Scope:** document new and modified code; when editing a file, add missing module docs and document public symbols you touch.

## Architecture

**Development** — dual server (browser uses `:5173`):

```
Browser (:5173) → Vite → /api/* proxy → Flask (:5000)
```

**Production** — single Flask server serves Vite build from `backend/static/`:

```
Browser (:5000) → Flask
  ├─ /api/*     → blueprints (auth, routes)
  └─ /*         → SPA fallback (backend/static/index.html + assets)
```

**Production deploy** — `.github/workflows/docker-publish.yml` runs CI, publishes a private GHCR image, then `scripts/deploy-hostinger.sh` updates Hostinger VM `1136636` / Docker project `dsfor`. The script asserts `GET /api/health` `version` equals `github.sha` and rolls back to the previous `VWF_IMAGE` on failure. The only deploy secret is `HOSTINGER_API_TOKEN`.

Flask uses a custom SQLAlchemy singleton (`db_session`), not Flask-SQLAlchemy.

Canonical entry points: `backend/__init__.py` (`create_app`), `frontend/src/js/app.js` (`createSpaApp`).

## Git and deploy

- **Never push to `master`** (or any default branch). Never merge unless the user explicitly asks.
- **One PR per change**, targeting `master`.
- Branch protection requires the branch to be **up to date** with `master` and these checks green: `backend`, `frontend`, `build-and-push`, plus `lint` (shellcheck / actionlint).
- Every merge to `master` **auto-deploys**: CI → private GHCR image `ghcr.io/elizio/vanilla-webapp-framework:sha-<full>` → `scripts/deploy-hostinger.sh` (Hostinger VM `1136636` / Docker project `dsfor`).
- The deploy asserts `GET /api/health` returns 200 with `status == "ok"` and `version ==` the merge SHA, then checks the home page. On failure it POSTs the previous environment (`VWF_IMAGE`) and re-checks health.
- Say in the PR whether runtime behavior changes. Docs-only and test-only PRs still rebuild and deploy; they should be a no-op for the running app.
- Production config lives on the VPS. Do not commit secrets or paste real env values. The only deploy secret in GitHub is `HOSTINGER_API_TOKEN`.
- Actions are SHA-pinned. Dependabot updates `pip`, `npm` (`/frontend`), `github-actions`, and `docker` weekly.

## Full-stack feature checklist

When adding a feature that spans backend and frontend:

1. **Model** (if needed) — `backend/models/`, extend `db.Base`
2. **API** — new or extended blueprint in `backend/api/`, Swagger docstring
3. **Auth** — use `@token_required` for protected routes (see `backend/api/auth.py`)
4. **Test** — `backend/tests/test_*.py` with `test_client` + `test_db` fixtures
5. **Controller** — `frontend/src/js/controllers/<feature>.js`
6. **Template** — `frontend/src/templates/pages/<feature>.hbs` (Alpine markup)
7. **Registry** — register in `frontend/src/js/pages.js` (controller + `?raw` template import)
8. **Navigation** — wire `loadPage('view-container', '<pageKey>')` in menu template

Backend-first: ship API + tests before frontend integration.

**Billing:** optional Lemon Squeezy demo is wired. Human dashboard setup → [docs/billing-configuration.md](docs/billing-configuration.md). To add or swap payment providers in code → **Billing — add a payment provider** in [backend/AGENTS.md](backend/AGENTS.md).

## Remaining follow-ups

| Item | Status |
|------|--------|
| Flask-SQLAlchemy migration | Deferred — stay on `db_session` singleton |
| SSR/prerender for SEO-heavy forks | Documented recipe in [frontend/AGENTS.md](frontend/AGENTS.md) |
| Unused `workflow_dispatch` stub | `.github/workflows/deploy.yml` is not the production deploy path |

Shipped and verified against the code: cookie auth + CSRF, CORS origin lockdown (`APP_BASE_PATH` cookie Path, HSTS without `includeSubDomains`), OAuth linking (Google only when `email_verified`; Facebook never links by email), `/api/health` `{status, db, version}` with SHA assertion + rollback, webhook reliability, History API routing, repo hygiene, container hardening (UID 10001, migrate-once entrypoint, stdout logs, image `HEALTHCHECK`), deploy script + SHA-pinned actions + `lint`.

## Agent principles

- Minimize scope; match existing patterns in neighboring files
- Reference canonical files (`@backend/api/routes.py`) instead of copying code
- Backend work → read [backend/AGENTS.md](backend/AGENTS.md)
- Frontend work → read [frontend/AGENTS.md](frontend/AGENTS.md)
- Standards (PEP 8, Blueprints, Tailwind) → [.cursor/rules/](.cursor/rules/)
- README how-tos → update [README.md](README.md) when triggers match; see Documentation policy above
- In-code docs → follow [.cursor/rules/documentation.mdc](.cursor/rules/documentation.mdc)
