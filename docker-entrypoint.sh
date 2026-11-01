#!/bin/sh
# Migrate once when launching the app, then exec gunicorn (or the given command).
# Do not enable xtrace: it would print secret environment values.
set -eu

is_app_server=0
if [ "$#" -eq 0 ] || [ "$1" = "gunicorn" ]; then
  is_app_server=1
fi

if [ "$is_app_server" -eq 1 ]; then
  missing=""
  for var in FLASK_SECRET JWT_SECRET DATABASE_URI; do
    eval "val=\${$var:-}"
    if [ -z "$val" ]; then
      missing="$missing $var"
    fi
  done
  if [ -n "$missing" ]; then
    echo "error: missing required environment variable(s):$missing" >&2
    echo "error: set each variable in the container environment; values are not printed." >&2
    exit 1
  fi

  echo "Running migrations"
  if ! alembic -c backend/alembic.ini upgrade head; then
    echo "error: migrations failed" >&2
    exit 1
  fi

  port="${PORT:-5000}"
  exec gunicorn \
    --bind "0.0.0.0:${port}" \
    --workers 2 \
    --access-logfile - \
    --error-logfile - \
    backend.app:app
fi

exec "$@"
