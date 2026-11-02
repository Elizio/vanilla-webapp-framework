# Architecture — Vanilla WebApp Framework

Codemap for agents and humans. How-to commands stay in [README.md](README.md) and [AGENTS.md](AGENTS.md). Decisions live in [docs/adr/](docs/adr/).

## Layers

```
HTTP (Flask blueprints)
  → services (billing, auth helpers)
    → models (SQLAlchemy, data-only)
      → db_session (custom singleton, not Flask-SQLAlchemy)
```

| Layer | Lives in | Rule |
|-------|----------|------|
| Routes | `backend/api/*.py`, `backend/web_routes.py` | Blueprints + Flasgger YAML. SPA `/` and error handlers in `web_routes.py`. |
| Services | `backend/billing/`, `backend/api/session_auth.py`, `backend/api/refresh_tokens.py` | Orchestration, no HTML. |
| Models | `backend/models/` | Columns and relationships only. |
| Config | `backend/config/` | `AppConfig` / `UserConfig` from env. |
| SPA | `frontend/src/js/` + `frontend/src/templates/` | Alpine controllers + `?raw` HTML fragments. |

Canonical entry points: `backend/__init__.py` (`create_app`), `frontend/src/js/app.js` (`createSpaApp`).

## Runtime flows

**Development** (browser uses `:5173`):

```
Browser (:5173) → Vite → /api/* proxy → Flask (:5000)
```

**Production** (single Flask process):

```
Browser (:5000) → Flask
  ├─ /api/*  → blueprints
  └─ /*      → SPA fallback (backend/static/index.html + assets)
```

Vite `npm run build` writes into `backend/static/` (`emptyOutDir: true`). The Docker image copies that tree. `APP_PROFILE=production flask run` does **not** migrate — run `make migrate` first. Production containers migrate once in `docker-entrypoint.sh`.

## CI → GHCR → Hostinger

1. PR/push CI (`.github/workflows/ci.yml`): `backend` (`check-pins`, `audit-python`, ruff/mypy, `prove-ruff-fail` / `prove-mypy-fail`, `migrations-check`, `test-backend`), `frontend` (`audit-frontend`, biome, `prove-biome-fail`, `build-frontend`, `test-frontend`), `lint` (shellcheck, actionlint, gitleaks, `prove-gitleaks-fail`).
2. `build-and-push` (`.github/workflows/docker-publish.yml`) builds with `load: true`, runs `make smoke`, then pushes off PRs (`ghcr.io/elizio/vanilla-webapp-framework:sha-<full>`).
3. On `master` push, `scripts/deploy-hostinger.sh` updates Hostinger VM `1136636` / Docker project `dsfor` and asserts `GET /api/health` `version ==` the merge SHA. Rollback is the previous `VWF_IMAGE`.
4. Required check names stay `backend`, `frontend`, `build-and-push` (plus `lint`). Never push to `master`.

## Add a full-stack feature

1. Model in `backend/models/` (`db.Base`) if needed.
2. Blueprint in `backend/api/` with Swagger `---` block.
3. `@token_required` for protected routes.
4. pytest in `backend/tests/`.
5. Controller `frontend/src/js/controllers/<feature>.js`.
6. Template `frontend/src/templates/pages/<feature>.hbs`.
7. Register in `frontend/src/js/pages.js` (controller + `?raw`).
8. Wire `loadPage('view-container', '<pageKey>')` in the menu.

Backend-first: ship API + tests before the SPA page.

## Add an API endpoint

Create or extend a blueprint in `backend/api/`, register it in `create_app()`, add `backend/tests/test_<feature>.py`. Copy the Swagger block from `backend/api/routes.py`. SPA fallback and `@app.errorhandler` stay in `web_routes.py`.

## Add a payment provider

Billing is provider-agnostic. Plans, entitlements, credits, and the SPA billing page stay in the app. Each processor is a thin adapter.

| Layer | Role | Provider-specific? |
|-------|------|--------------------|
| `billing/plans.py` | Catalog (`outcome`: entitlement / credits / none) | No — provider ids from env var **names** |
| `billing/providers/*.py` | Checkout + webhook verify/parse | Yes |
| `billing/service.py` | Validate checkout, apply webhook (idempotent) | No |
| `models/billing_*` | Entitlements, events, credits | No |
| `api/billing.py` | HTTP; frontend talks only here | Webhook route per provider |

Contract: `backend/billing/providers/base.py`. Working adapter: `lemon_squeezy.py`. Outline: `stripe.py`.

1. Implement `BillingProvider` (`name`, `is_configured`, `create_checkout`, `verify_webhook`, `parse_webhook` → `BillingWebhookResult` with a stable `event_id`).
2. Register in `backend/billing/providers/__init__.py` `_PROVIDERS`.
3. Add a `providers` entry on each plan (env var names, never hardcoded ids).
4. Add env keys to `AppConfig`, `.env.example`, [docs/billing-configuration.md](docs/billing-configuration.md). README env table only.
5. Webhook route in `api/billing.py`. `handle_webhook` uses `BILLING_PROVIDER` today; a second concurrent provider needs an optional provider key.
6. Tests in `backend/tests/test_billing.py` (mock HTTP; signed payloads; idempotency).

`parse_webhook` mapping: `entitlement` → `upsert_entitlement()`; `credits` → `add_credits()`; `none` → audit only. Do not change entitlement tables, `frontend/src/js/controllers/billing.js`, or `outcome` semantics.

## Auth notes

Cookie session + CSRF (`GET /api/csrf` then `X-CSRF-Token`). Short-lived access JWT in `auth_token` (`user_id`, `iat`, `exp`, `tv`; default 900 s) plus a rotating opaque `refresh_token` cookie (`Path={APP_BASE_PATH}/api/auth`, `SameSite=Strict`, `Secure` in production). Refresh rows live in `refresh_tokens` (Alembic **009**). `tv` must match `users.token_version` (Alembic **008**, default 0); a missing `tv` counts as 0. `POST /api/auth/refresh` rotates the cookie (reuse after a 30 s grace window revokes the family). `POST /api/auth/logout` revokes that family and clears both cookies. `POST /api/auth/logout-all` bumps `token_version` and revokes every family. Deprecated `POST /api/logout` still clears cookies. Remember-me (login checkbox) persists the refresh cookie for 30 days; unchecked is a browser-session cookie with 24 h server TTL. OAuth counts as remember-me. `auth_device` survives logout. Inactive users get **403** `ACCOUNT_INACTIVE` (including refresh). Bearer is for access tokens only. Google links by email only when `email_verified` **and** the local account is already verified; an unverified local claim is cleared so Google keeps the address. Facebook never links by email (duplicate addresses are stored as `NULL`). `users.email` is unique (NULLs allowed, Alembic **010**). `users.password_hash` is `String(255)`.

Email sending is pluggable (`backend/email/`): `EMAIL_BACKEND=console` (dev/tests outbox) or `smtp` (stdlib `smtplib`, STARTTLS or SSL, Resend-compatible). Unset `EMAIL_BACKEND` / missing SMTP vars: sign-up and login unchanged, password reset **503** `EMAIL_NOT_CONFIGURED`, no startup crash. `GET /api/auth/capabilities` exposes `{email_configured, password_reset, email_verification}`. When sending is on, register requires a unique normalized email and does not set a session cookie; `POST /api/auth/verify-email` consumes a hashed single-use token (24 h) and logs the user in. `POST /api/auth/password/forgot` always returns 202 for known and unknown addresses (rate-limited in `rate_limit_counters`); `POST /api/auth/password/reset` (1 h token) sets the password, calls `bump_token_version()`, and `revoke_all_families()`. Tokens live in `auth_tokens` (Alembic **010**). Links are `{FRONTEND_URL}/?verify_token=` or `/?reset_token=` (absolute URL, production subpath included). Human SMTP setup: [docs/email-configuration.md](docs/email-configuration.md).

Auth rate limits (login + register) use **fixed windows** in `rate_limit_counters` (approximate; a window-edge burst can admit ~2×): per client IP (IPv6 /64); trusted `auth_device` cookie (5 / 15 min per username+device); untrusted username+subnet (IPv4 /24, IPv6 /64) plus global per-username backoff (**15 password checks / 900 s**). Keys are stored as SHA-256 hex. `RATELIMIT_ENABLED` is on in production/development and off in testing. `TRUST_PROXY=1` plus `TRUST_PROXY_HOPS` (**default 1**, matching prod Caddy) select `request.remote_addr`. Appending the client to `X-Forwarded-For` is fine with `x_for=1`. Decision: [docs/adr/0006-auth-rate-limit-store.md](docs/adr/0006-auth-rate-limit-store.md).

Database: `from backend.db_repository.database import db, db_session`. New reads use `db_session.get(Model, id)`. Wrap writes in try/commit/rollback.

## Add a SPA page

1. Template in `frontend/src/templates/pages/` — Alpine only, no Handlebars.
2. Controller in `frontend/src/js/controllers/`.
3. Register in `pages.js` with a `seo` block (`visibility`: `public` | `app` | `auth`).
4. Navigate with `loadPage('view-container', '<pageKey>')`.

`.hbs` files are static HTML + Alpine, imported with Vite `?raw`. There is no `handlebars` dependency. SEO: `applySeo()` in `frontend/src/js/seo.js`; `SEO_MODE` (`auth-first` / `public-first`) also drives `/robots.txt`. i18n: `en` + `pt-BR` in `frontend/src/locales/`.

## Documentation policy

Human how-tos live in [README.md](README.md). Enforceable minimums: [.cursor/rules/documentation.mdc](.cursor/rules/documentation.mdc).

| Trigger | README section |
|---------|----------------|
| New env var or config | Environment Variables + `.env.example` |
| Database / migration | Project setup + Configure & operate |
| Setup / run command | Project setup / Run by environment |
| OAuth / billing / email dashboard | Configure & operate (link the docs; do not duplicate steps) |
| Deploy / CI | Run by environment, Deployment |

Do not copy AGENTS recipes into README. Do not claim unimplemented deploy targets.

In-code: module docstring on every Python file you touch; Google-style + type hints on public Python; Flasgger `---` on routes; file-level JSDoc on exported JS.
