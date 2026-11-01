# Developer shortcuts. Production containers migrate in docker-entrypoint.sh.
.PHONY: migrate

migrate:
	alembic -c backend/alembic.ini upgrade head
