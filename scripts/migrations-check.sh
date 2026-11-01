#!/usr/bin/env bash
# Fail if SQLAlchemy models have drifted from Alembic revisions.
# Uses a throwaway SQLite file so CI's sqlite:///:memory: is not inherited.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

export DATABASE_URI="sqlite:///${tmpdir}/alembic-check.db"
export APP_PROFILE="${APP_PROFILE:-testing}"
export FLASK_SECRET="${FLASK_SECRET:-ci-alembic-flask}"
export JWT_SECRET="${JWT_SECRET:-ci-alembic-jwt}"

cd "$ROOT"
alembic -c backend/alembic.ini upgrade head
alembic -c backend/alembic.ini check
alembic -c backend/alembic.ini downgrade -1
alembic -c backend/alembic.ini upgrade head
