# Developer shortcuts. Production containers migrate in docker-entrypoint.sh.
# `make setup && make check` is the local equivalent of CI.
.PHONY: setup dev test lint format typecheck check migrate audit \
	lint-python lint-frontend lint-shell lint-tools \
	test-backend test-frontend

export PATH := $(CURDIR)/.tools:$(PATH)
PIP ?= pip
PYTHON ?= python

setup:
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e . --no-deps
	cd frontend && npm ci
	$(MAKE) lint-tools

lint-tools:
	./scripts/install-lint-tools.sh

lint-python:
	ruff check backend conftest.py setup.py
	ruff format --check backend conftest.py setup.py
	mypy backend

typecheck:
	mypy backend

lint-frontend:
	cd frontend && npm run lint

lint-shell: lint-tools
	shellcheck scripts/*.sh docker-entrypoint.sh
	actionlint
	gitleaks detect --source . --verbose --redact

lint: lint-python lint-frontend lint-shell

format:
	ruff check --fix backend conftest.py setup.py
	ruff format backend conftest.py setup.py
	cd frontend && npm run format

test-backend:
	pytest

test-frontend:
	cd frontend && npm run test

test: test-backend test-frontend

audit:
	pip-audit -r requirements.txt
	cd frontend && npm audit --omit=dev --audit-level=high

check: lint test

dev:
	@echo "Run these in two terminals from the repo root:"
	@echo "  flask run"
	@echo "  cd frontend && npm run dev"
	@echo "Then open http://localhost:5173"

migrate:
	alembic -c backend/alembic.ini upgrade head
