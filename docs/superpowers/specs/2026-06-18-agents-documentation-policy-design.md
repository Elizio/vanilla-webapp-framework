# AGENTS.md Documentation Policy — Design Spec

**Date:** 2026-06-18  
**Status:** Approved (brainstorming)  
**Scope:** Root `AGENTS.md`, sub-guides, `.cursor/rules/`, one-time README drift fix

## Problem

Agent guidance tells agents where human onboarding lives (`README.md`) but not when or how to keep it accurate. Documentation standards are scattered across Rule 4.4, backend Swagger rules, and generic README bullets. Known drift exists (DigitalOcean claim, missing OAuth env vars in README, outdated project tree).

## Goals

1. Agents evaluate and update `README.md` when changes affect human onboarding or when obvious drift is discovered in scope.
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
| `README.md` | Humans | Onboarding, features, setup, contributing |
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

### Triggers

Agents evaluate `README.md` before claiming work done when changes touch:

| Trigger | README sections to check |
|---------|---------------------------|
| New env var or config | Getting Started → Environment Variables; cross-check `.env.example` |
| Setup / run / test command change | Getting Started, Testing |
| New user-facing feature or API surface | Features, Tech Stack (if applicable) |
| Project layout change | Project Structure tree |
| Deployment / CI change | Deployment, DevOps bullets |
| Capability added or removed | Features — remove unimplemented claims |

### When NOT to update README

Pure refactors, internal-only changes, test-only edits, or agent-recipe changes that belong in AGENTS only.

### Process

Added to root `AGENTS.md` verification checklist:

1. Scan triggers against the diff.
2. If any match → update README (and `.env.example` if env-related).
3. If no trigger matches but drift is noticed while reading → fix in the same PR when scope permits.
4. Do not copy AGENTS content into README.

### One-time README cleanup (implementation pass)

- Remove or qualify DigitalOcean deployment claim until automation exists.
- Add OAuth and redirect env vars (align with `.env.example` and root AGENTS).
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
| `AGENTS.md` | New "Documentation policy" section; README sync triggers; expanded verification checklist; updated doc map |
| `backend/AGENTS.md` | "Code documentation" section with Python examples; link to Swagger section |
| `frontend/AGENTS.md` | "Code documentation" section with JSDoc examples |
| `.cursor/rules/documentation.mdc` | New — README sync, module docs, public API docs, Swagger on routes |
| `.cursor/rules/project-structure.mdc` | Rule 4.4 expanded to reference `documentation.mdc` |
| `.cursor/rules/backend-rules.mdc` | Rule 1.13: module + public API docstrings, type hints |
| `.cursor/rules/frontend-rules.mdc` | Rule 2.12: JSDoc on exported modules/functions |
| `README.md` | One-time drift fix; Documentation section update |

## Verification

After implementation:

- [ ] All listed files updated and cross-linked
- [ ] README matches `.env.example` and root AGENTS env table for OAuth vars
- [ ] No DigitalOcean claim without "not yet implemented" qualifier
- [ ] Spot-check: `backend/api/routes.py` pattern cited in backend AGENTS; `frontend/src/js/app.js` cited in frontend AGENTS
- [ ] `pytest` and `cd frontend && npm run build && npm run test` still pass (doc-only changes should not break tests)

## Decisions log

| Decision | Choice |
|----------|--------|
| Scope | Full stack: root AGENTS + sub-guides + `.cursor/rules` |
| README sync trigger | Onboarding + features + fix drift when touching related code |
| Docstring depth | Level B — module docs everywhere; public APIs documented; type hints on Python public signatures |
| Architecture | Layered policy (option C) |
