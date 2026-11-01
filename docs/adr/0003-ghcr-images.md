# ADR 0003: Publish a multi-stage image to GHCR

## Status

Accepted

## Context

Production is a single container: Vite assets + Gunicorn. The image must be reproducible and free of dev tools.

## Decision

- Multi-stage `Dockerfile`: Node 20 builds the SPA, Python 3.10-slim runs it as UID 10001.
- Tags: `ghcr.io/elizio/vanilla-webapp-framework:sha-<full>` and `latest` on `master`.
- `APP_VERSION` is the git SHA (`ARG GIT_SHA` last so earlier layers cache).
- CI `build-and-push` is the only publisher. Dev tools (pytest, ruff, …) must not be in the image.

## Consequences

- Merges rebuild and publish. Docs-only PRs still deploy a new image (should be a no-op for the app).
- Python/node base-image majors are a deliberate PR, not a Dependabot minor bump.
