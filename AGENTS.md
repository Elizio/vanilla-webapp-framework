# Agent Guide — Vanilla WebApp Framework

Flask REST API + vanilla JavaScript SPA (Alpine.js, Tailwind, Vite). Human onboarding lives in [README.md](README.md). Coding standards live in [.cursor/rules/](.cursor/rules/). This file covers what agents need to run, verify, and extend the project.

## Documentation map

| Doc | Scope |
|-----|-------|
| **This file** | Global setup, verification, full-stack checklist, debt summary |
| [docs/oauth-configuration.md](docs/oauth-configuration.md) | OAuth setup (human): Google, Facebook |
| [backend/AGENTS.md](backend/AGENTS.md) | Flask, DB, JWT, pytest recipes |
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
└── Dockerfile         # Multi-stage production image
```

## Environment setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Create `.env` in the project root:

| Variable | Purpose |
|----------|---------|
| `FLASK_SECRET` | Flask sessions / CSRF |
| `JWT_SECRET` | JWT signing |
| `DATABASE_URI` | DB connection string |
| `PROJECT_FOLDER` | Log file directory |
| `APP_PROFILE` | `development`, `testing`, or `production` |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Google OAuth (optional) |
| `FACEBOOK_CLIENT_ID` / `FACEBOOK_CLIENT_SECRET` | Facebook OAuth (optional) |
| `FRONTEND_URL` | SPA URL after OAuth (default `http://localhost:5173` in dev) |
| `OAUTH_REDIRECT_BASE` | OAuth callback base URL (default `http://localhost:5173` in dev) |
| `SEO_MODE` | `auth-first` (default) or `public-first`; frontend meta defaults + `/robots.txt` |

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
- [ ] Production smoke: `cd frontend && npm run build && APP_PROFILE=production flask run` → `:5000`
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
| **Configure & operate** | OAuth, logs, Swagger, Alembic, CI, or troubleshooting steps change |

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
| OAuth or auth flow change | Project setup + Configure & operate |
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

Flask uses a custom SQLAlchemy singleton (`db_session`), not Flask-SQLAlchemy.

Canonical entry points: `backend/__init__.py` (`create_app`), `frontend/src/js/app.js` (`createSpaApp`).

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

## Remaining follow-ups

| Item | Status |
|------|--------|
| DigitalOcean deploy automation | Not implemented (devops rule 3.4) |
| Login/logout full-page reload | Still uses `window.location.href = '/'` |
| Flask-SQLAlchemy migration | Deferred — stay on `db_session` singleton |

Resolved in this foundation pass: production static pipeline, page registry, Alembic, CI, slim Docker, cursor rules alignment.

## Agent principles

- Minimize scope; match existing patterns in neighboring files
- Reference canonical files (`@backend/api/routes.py`) instead of copying code
- Backend work → read [backend/AGENTS.md](backend/AGENTS.md)
- Frontend work → read [frontend/AGENTS.md](frontend/AGENTS.md)
- Standards (PEP 8, Blueprints, Tailwind) → [.cursor/rules/](.cursor/rules/)
- README how-tos → update [README.md](README.md) when triggers match; see Documentation policy above
- In-code docs → follow [.cursor/rules/documentation.mdc](.cursor/rules/documentation.mdc)
