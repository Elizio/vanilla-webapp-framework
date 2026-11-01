# Agent Guide — Vanilla WebApp Framework

Flask REST API + vanilla JavaScript SPA (Alpine.js, Tailwind, Vite). Human onboarding: [README.md](README.md). Architecture: [ARCHITECTURE.md](ARCHITECTURE.md). ADRs: [docs/adr/](docs/adr/). Standards: [.cursor/rules/](.cursor/rules/).

## Documentation map

| Doc | Scope |
|-----|-------|
| **This file** | Setup, `make` loop, verification, follow-ups |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Layers, request flow, feature recipes, README sync triggers |
| [docs/adr/](docs/adr/) | Why Flask, Vite, GHCR, Hostinger, Phase 1 tools |
| [CONTRIBUTING.md](CONTRIBUTING.md) | PR/issue templates and review expectations |
| [docs/oauth-configuration.md](docs/oauth-configuration.md) | OAuth (human): Google, Facebook |
| [docs/billing-configuration.md](docs/billing-configuration.md) | Billing (human): Lemon Squeezy, webhooks |
| [docs/template-placeholders.md](docs/template-placeholders.md) | Names rewritten by `make init` |
| [backend/AGENTS.md](backend/AGENTS.md) | Flask / DB / JWT / pytest map |
| [frontend/AGENTS.md](frontend/AGENTS.md) | Vite / Alpine / controllers map |
| [.cursor/rules/documentation.mdc](.cursor/rules/documentation.mdc) | README how-to + in-code docs |

## Repository layout

```
vanilla-webapp-framework/
├── backend/              # Flask API (backend/AGENTS.md)
├── frontend/             # Vite SPA (frontend/AGENTS.md)
├── ARCHITECTURE.md       # Codemap and recipes
├── docs/adr/             # Architecture decision records
├── .cursor/rules/        # Cursor rules (.mdc)
├── .env                  # Required secrets (not committed)
├── requirements.txt      # Python runtime pins
├── requirements-dev.txt  # runtime + ruff, mypy, pytest, pre-commit
├── pyproject.toml        # Ruff, mypy, coverage floor
├── Makefile              # setup, lint, format, test, check, migrate, migrations-check, smoke, init
├── .pre-commit-config.yaml
├── setup.py              # pip install -e .
├── .github/workflows/    # CI (backend, frontend, lint) + image smoke in build-and-push
├── scripts/              # pins, deploy, lint-tool install, migrations-check.sh, smoke-image.sh, init-project
└── Dockerfile            # Multi-stage production image
```

## Environment setup

```bash
python -m venv .venv
source .venv/bin/activate
make setup
```

`make setup` matches CI: `requirements-dev.txt`, `pip install -e . --no-deps`, frontend `npm ci`, pinned shellcheck/actionlint/gitleaks into `.tools/`. Copy `.env.example` to `.env`. Operator table: [README.md](README.md). Do not invent keys.

OAuth redirect: `{OAUTH_REDIRECT_BASE}/api/auth/{provider}/callback` (dev: `http://localhost:5173/api/auth/google/callback` so the Vite proxy keeps the session cookie).

## Development workflow

Two terminals from the repo root: `flask run` (`:5000`) and `cd frontend && npm run dev` (`:5173`). Use **`:5173`** in the browser. Vite proxies `/api/*`. Swagger: `http://localhost:5000/docs`.

## Developer commands (`make`)

| Target | What it runs |
|--------|----------------|
| `make setup` | `requirements-dev.txt` + editable install + frontend `npm ci` + lint binaries |
| `make check-pins` | `scripts/check_pins.py` |
| `make audit` | `audit-python` (`pip-audit`) + `audit-frontend` (`npm audit --omit=dev`) |
| `make lint` | Ruff, mypy, Biome, shellcheck, actionlint, gitleaks |
| `make prove-linters-fail` | `prove-ruff-fail`, `prove-mypy-fail`, `prove-biome-fail`, `prove-gitleaks-fail` |
| `make migrations-check` | `alembic upgrade head` + `check` + `downgrade -1` + `upgrade head` on throwaway SQLite |
| `make build-frontend` | Vite build + `backend/static/index.html` exists |
| `make test` | `test-backend` (`pytest` + `fail_under`) + `test-frontend` (`npm run test:coverage`) |
| `make check` | `check-pins` + `audit` + `lint` + `prove-linters-fail` + `migrations-check` + `build-frontend` + `test` — same gates as CI except Docker `smoke` |
| `make smoke` | Built image, dummy secrets, SQLite, curl `/api/health` + `/` (`IMAGE=`, Docker; `build-and-push` before push) |
| `make format` | Ruff + Biome autofixes |
| `make migrate` | `alembic -c backend/alembic.ini upgrade head` |
| `make init` | Rewrite template names (`NAME=my-app`), reset plans, run `make check`. See [docs/template-placeholders.md](docs/template-placeholders.md) |
| `make typecheck` | `mypy backend` |

Biome lints JS and JSON only — not `.hbs` templates. `frontend/src/styles/main.css` is excluded (Tailwind stays on Vite/PostCSS). New Python modules inherit strict mypy in `pyproject.toml`; do not add them to the ignore list.

## Coverage ratchet

Floors live in `[tool.coverage.report] fail_under` (`pyproject.toml`) and `test.coverage.thresholds` (`frontend/vitest.config.js`). Enforced by the existing `backend` / `frontend` jobs and by `make test`. Raise a floor when coverage goes up ≥1 point; never lower one without a PR justification.

## Verification checklist

- [ ] `make check`
- [ ] `cd frontend && npm run build && npm run test`
- [ ] App loads at `:5173` (`npm run dev`)
- [ ] Production smoke: frontend build + `make migrate` + `APP_PROFILE=production flask run`
- [ ] New endpoints have Swagger + pytest
- [ ] README / `.env.example` updated when triggers in [ARCHITECTURE.md](ARCHITECTURE.md) match
- [ ] New/modified modules have docs per documentation.mdc

## Git and deploy

- Never push to `master`. One PR per change. Branch protection: up to date + `backend`, `frontend`, `build-and-push`, `lint`.
- `build-and-push` runs `make smoke` on the loaded image before push (PRs smoke without publishing).
- Merge auto-deploys: CI → `ghcr.io/elizio/vanilla-webapp-framework:sha-<full>` → `scripts/deploy-hostinger.sh` (VM `1136636` / `dsfor`). Health `version` must equal the merge SHA.
- Say whether runtime behavior changes. No secrets in the repo. Actions are SHA-pinned.

## Remaining follow-ups

| Item | Status |
|------|--------|
| Flask-SQLAlchemy migration | Deferred — stay on `db_session` |
| SSR/prerender for SEO-heavy forks | Recipe in [frontend/AGENTS.md](frontend/AGENTS.md) |
| Coverage floor | #18 (shipped) |
| DB-aware `/api/health` | #16 (shipped) |
| Image `HEALTHCHECK` | #19 (shipped) |
| Least-privilege token + SHA-pinned actions | #22 (shipped) |
| structlog + `X-Request-ID` | Not filed |
| docker-compose / devcontainer | Not filed |

## Agent principles

- Minimize scope; match neighboring files; reference canonical paths instead of copying.
- Backend → [backend/AGENTS.md](backend/AGENTS.md). Frontend → [frontend/AGENTS.md](frontend/AGENTS.md). Recipes → [ARCHITECTURE.md](ARCHITECTURE.md).
- README how-tos: update when [ARCHITECTURE.md](ARCHITECTURE.md) triggers match.
