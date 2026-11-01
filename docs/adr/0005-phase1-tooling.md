# ADR 0005: Ruff, mypy, Biome, gitleaks, Makefile

## Status

Accepted (Phase 1 of #13)

## Context

CI and local loops had drifted (flake8, unpinned extras, no single `make check`). Agents need one command that matches CI.

## Decision

| Area | Tool |
|------|------|
| Python lint/format | Ruff (`pyproject.toml`) |
| Python types | mypy 3.10, per-module `ignore_errors` baseline (no blanket ignore) |
| Frontend lint/format | Biome (JS + JSON) |
| Secrets | gitleaks in pre-commit and CI (`fetch-depth: 0`) |
| Hooks | pre-commit (Ruff, Biome, gitleaks, file hygiene) |
| Task runner | `Makefile` (`setup`, `lint`, `test`, `check`, `migrate`, …) |
| Dependency updates | Dependabot (owned by #15) |

## Consequences

- `make setup && make check` is the local CI loop.
- New backend modules inherit strict mypy; do not add them to the ignore list.
- Coverage floors (#18) live in `pyproject.toml` / `frontend/vitest.config.js` and run inside the existing jobs.
