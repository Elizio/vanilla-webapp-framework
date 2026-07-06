# AGENTS.md Documentation Policy — Design Spec

**Date:** 2026-06-18  
**Status:** Approved  
**Scope:** Root `AGENTS.md`, sub-guides, `.cursor/rules/`, one-time README drift fix

## Problem

Agent guidance tells agents where human onboarding lives (`README.md`) but not when or how to keep it accurate. Documentation standards are scattered across Rule 4.4, backend Swagger rules, and generic README bullets. Known drift exists (DigitalOcean claim, missing OAuth env vars in README, outdated project tree).

## Goals

1. Agents evaluate and update `README.md` when changes affect human onboarding or when obvious drift is discovered in scope — especially **how-to guides** for setup, running in each environment, and other steps needed to configure and run the solution.
2. Agents document code with docstrings/JSDoc following consistent, enforceable standards.
3. Policy is layered: README (humans) → AGENTS (agent ops) → rules (enforcement) → in-code docs (implementation).

## Non-goals

- Repo-wide retroactive documentation of untouched legacy files
- Duplicating AGENTS recipes in README
- Adding linter tooling (pydocstyle, eslint-plugin-jsdoc) in this pass
- Changing Swagger/Flasgger behavior

## Documentation roles

| Layer | Audience | Content |
|-------|----------|---------|
| `README.md` | Humans | Features overview, **how-to guides** (setup, run per environment, configure), contributing |
| `AGENTS.md` (+ sub-guides) | Agents | When to update README, verification steps, code-doc expectations, examples |
| `.cursor/rules/*.mdc` | Cursor enforcement | Short enforceable rules (what, not why) |
| In-code docs | Developers + agents | Docstrings, JSDoc, Swagger YAML on routes |

**Boundary rule:** AGENTS never duplicates README prose — it instructs agents *when and what* to update. README does not contain agent recipes; optional one-liner may point contributors to AGENTS.

## Approach

**Layered policy (recommended option C):**

- Root `AGENTS.md` owns narrative policy and verification checklist items.
- New `.cursor/rules/documentation.mdc` holds cross-cutting enforceable minimums.
- `backend/AGENTS.md` and `frontend/AGENTS.md` hold language-specific examples.
- Existing rules files get targeted additions; Rule 4.4 points to the new rule file.

## README sync policy

`README.md` is the canonical **how-to** for humans. Agents must keep these guides accurate and runnable — not just feature lists.

### Required how-to categories

README must maintain up-to-date sections (headings may vary; content must exist):

| Category | What humans need to do | Example topics |
|----------|------------------------|----------------|
| **1. Project setup** | Install deps, configure env, initialize database | venv + `pip install -e .`, `.env` / `.env.example`, `DATABASE_URI`, `APP_PROFILE`, `PROJECT_FOLDER`, OAuth vars, Alembic/`init_db` notes |
| **2. Run by environment** | Start the app in each supported mode | Development (dual server `:5173` + `:5000`), production (`npm run build` + `APP_PROFILE=production flask run`), Docker, testing (`pytest`, frontend tests) |
| **3. Configure & operate** | Other steps required to configure or run | OAuth redirect URIs, log paths, Swagger URL, CI expectations, migration commands, troubleshooting common setup failures |

AGENTS tells agents *when* to update these; README holds the step-by-step commands. Do not move how-to prose into AGENTS.

### Triggers

Agents evaluate `README.md` before claiming work done when changes touch:

| Trigger | README how-to / section to check |
|---------|----------------------------------|
| New env var or config | **Project setup** → Environment Variables; cross-check `.env.example` |
| Database or migration change | **Project setup** (DB init/migrate); **Configure & operate** (Alembic commands) |
| Setup / install command change | **Project setup** |
| Run / start command change | **Run by environment** (dev, production, Docker, test) |
| New `APP_PROFILE` or environment behavior | **Run by environment** for that profile |
| New user-facing feature or API surface | Features, Tech Stack (if applicable) |
| Project layout change | Project Structure tree |
| Deployment / CI change | **Run by environment** (Docker/production), Deployment bullets |
| OAuth or auth flow change | **Project setup** (vars), **Configure & operate** (redirect URIs) |
| Capability added or removed | Features — remove unimplemented claims |

### When NOT to update README

Pure refactors, internal-only changes, test-only edits, or agent-recipe changes that belong in AGENTS only.

### Process

Added to root `AGENTS.md` verification checklist:

1. Scan triggers against the diff.
2. If any match → update the relevant README **how-to** section (and `.env.example` if env-related).
3. Confirm all three how-to categories still have accurate, copy-pasteable steps (setup, run per environment, configure/operate).
4. If no trigger matches but a how-to is stale or missing → fix in the same PR when scope permits.
5. Do not copy AGENTS recipes into README — link or mirror commands only in human-oriented prose.

### One-time README restructure (implementation pass)

Reorganize Getting Started into explicit how-to subsections:

1. **Setup** — venv, install, `.env` table (all vars from `.env.example`), database notes (`DATABASE_URI`, dev `init_db` vs production Alembic).
2. **Run — development** — dual terminal commands, browser URL (`:5173`), Vite proxy note.
3. **Run — production** — build frontend, `APP_PROFILE=production flask run`, single-server URL.
4. **Run — Docker** — build/run with required `-e` flags.
5. **Run — testing** — `pytest`, frontend build + test.
6. **Configure** — OAuth redirect URIs, log directory, Swagger at `/docs`, optional provider setup.

Also:

- Remove or qualify DigitalOcean deployment claim until automation exists.
- Fix project structure tree (build output path, Alembic location, remove stale entries).
- Slim Documentation section: Swagger for API, in-code docs per AGENTS/rules.

## In-code documentation standards (level B)

### Python (`backend/**/*.py`)

| Element | Requirement |
|---------|-------------|
| Module | One-line `"""..."""` at top describing purpose |
| Public functions/classes | Google-style docstring: summary, `Args`, `Returns`, `Raises` when non-obvious |
| Type hints | On all public function signatures |
| API routes | Flasgger Swagger YAML block (`---`) — required, unchanged |
| Private helpers | Docstring only when logic is non-obvious |
| Tests | Module docstring; brief docstring on non-obvious test cases |

### JavaScript (`frontend/src/**/*.js`)

| Element | Requirement |
|---------|-------------|
| Module | JSDoc file-level `@module` or brief block comment |
| Exported functions/objects | JSDoc with `@param`, `@returns` when signature is not self-evident |
| Controllers | JSDoc on exported controller describing page role |
| Router (`app.js`) | Document `createSpaApp`, `loadPage`, non-trivial helpers |
| Templates (`.hbs`) | HTML comments only for non-obvious Alpine wiring |

### Scope rule

Document new and modified code. When editing an existing file, add missing module-level docs and document public symbols touched in that change. No repo-wide retroactive pass.

### Anti-patterns

- Restating the function name ("Gets the user" for `get_user`).
- Duplicating Swagger content in a separate docstring on route handlers.
- README-style essays in module docstrings.

## File changes

| File | Change |
|------|--------|
| `AGENTS.md` | New "Documentation policy" section; README how-to categories + sync triggers; expanded verification checklist; updated doc map |
| `backend/AGENTS.md` | "Code documentation" section with Python examples; link to Swagger section |
| `frontend/AGENTS.md` | "Code documentation" section with JSDoc examples |
| `.cursor/rules/documentation.mdc` | New — README how-to maintenance, sync triggers, module docs, public API docs, Swagger on routes |
| `.cursor/rules/project-structure.mdc` | Rule 4.4 expanded to reference `documentation.mdc` |
| `.cursor/rules/backend-rules.mdc` | Rule 1.13: module + public API docstrings, type hints |
| `.cursor/rules/frontend-rules.mdc` | Rule 2.12: JSDoc on exported modules/functions |
| `README.md` | Restructure into setup / run-by-environment / configure how-tos; drift fix; Documentation section update |

## Verification

After implementation:

- [ ] All listed files updated and cross-linked
- [ ] README has runnable how-tos for: project setup, each run environment (dev, production, Docker, test), and configure/operate steps
- [ ] README env table matches `.env.example` and root AGENTS env table (including OAuth vars)
- [ ] Database setup documented (dev `init_db` vs production Alembic)
- [ ] No DigitalOcean claim without "not yet implemented" qualifier
- [ ] Spot-check: `backend/api/routes.py` pattern cited in backend AGENTS; `frontend/src/js/app.js` cited in frontend AGENTS
- [ ] `pytest` and `cd frontend && npm run build && npm run test` still pass (doc-only changes should not break tests)

## Decisions log

| Decision | Choice |
|----------|--------|
| Scope | Full stack: root AGENTS + sub-guides + `.cursor/rules` |
| README sync trigger | Keep how-to guides current (setup, run per environment, configure/operate) + features + fix drift when touching related code |
| Docstring depth | Level B — module docs everywhere; public APIs documented; type hints on Python public signatures |
| Architecture | Layered policy (option C) |
