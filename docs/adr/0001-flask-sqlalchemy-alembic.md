# ADR 0001: Flask + SQLAlchemy singleton + Alembic

## Status

Accepted

## Context

The app needs a small REST API, ORM models, and production migrations. Flask-SQLAlchemy would hide the session lifecycle we already own.

## Decision

- Flask blueprints and a `create_app()` factory in `backend/__init__.py`.
- Custom SQLAlchemy singleton (`db`, `db_session`) in `backend/db_repository/database.py`, not Flask-SQLAlchemy.
- Alembic revisions under `backend/db_repository/migrations/`. Operators apply them with `make migrate` / `alembic -c backend/alembic.ini upgrade head`. Production migrates once in `docker-entrypoint.sh`.

## Consequences

- Agents add models on `db.Base` and write Alembic revisions for production schema changes.
- A Flask-SQLAlchemy migration stays deferred (see [AGENTS.md](../../AGENTS.md) follow-ups).
- `APP_PROFILE=production flask run` does not migrate; operators run `make migrate`.
