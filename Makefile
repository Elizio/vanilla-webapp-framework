# Developer shortcuts. Production containers migrate in docker-entrypoint.sh.
# `make setup && make check` is the local equivalent of CI.
.PHONY: setup dev test lint format typecheck check migrate audit \
	lint-python lint-frontend lint-shell lint-tools \
	test-backend test-frontend \
	check-pins audit-python audit-frontend build-frontend \
	migrations-check smoke \
	prove-ruff-fail prove-mypy-fail prove-biome-fail prove-gitleaks-fail \
	prove-linters-fail

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

check-pins:
	$(PYTHON) scripts/check_pins.py

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
	cd frontend && npm run test:coverage

test: test-backend test-frontend

audit-python:
	pip-audit -r requirements.txt

audit-frontend:
	cd frontend && npm audit --omit=dev --audit-level=high

audit: audit-python audit-frontend

build-frontend:
	cd frontend && npm run build
	test -f backend/static/index.html

migrations-check:
	./scripts/migrations-check.sh

smoke:
	./scripts/smoke-image.sh

prove-ruff-fail:
	@tmpdir=$$(mktemp -d); \
	echo 'import os' > "$$tmpdir/bad.py"; \
	ruff check --isolated "$$tmpdir/bad.py"; \
	status=$$?; rm -rf "$$tmpdir"; \
	test $$status -ne 0

prove-mypy-fail:
	@tmpdir=$$(mktemp -d); \
	printf '%s\n' '[mypy]' > "$$tmpdir/mypy.ini"; \
	printf '%s\n' 'def f(x: int) -> str:' '    return x' > "$$tmpdir/bad.py"; \
	mypy --config-file "$$tmpdir/mypy.ini" --no-incremental "$$tmpdir/bad.py"; \
	status=$$?; rm -rf "$$tmpdir"; \
	test $$status -ne 0

prove-biome-fail:
	@tmpdir=$$(mktemp -d); \
	printf '%s\n' '{"linter":{"enabled":true,"rules":{"preset":"recommended"}}}' > "$$tmpdir/biome.json"; \
	printf '%s\n' 'debugger;' > "$$tmpdir/bad.js"; \
	npx --prefix frontend biome check --config-path "$$tmpdir/biome.json" "$$tmpdir/bad.js"; \
	status=$$?; rm -rf "$$tmpdir"; \
	test $$status -ne 0

prove-gitleaks-fail:
	@tmpdir=$$(mktemp -d); \
	printf 'slack_token=%s-%s-%s-%s\n' xoxb 123456789012 1234567890123 abcdefghijklmnopqrstuvwx > "$$tmpdir/leak.txt"; \
	gitleaks detect --no-git --source "$$tmpdir"; \
	status=$$?; rm -rf "$$tmpdir"; \
	test $$status -ne 0

prove-linters-fail: prove-ruff-fail prove-mypy-fail prove-biome-fail prove-gitleaks-fail

check: check-pins audit lint prove-linters-fail migrations-check build-frontend test

dev:
	@echo "Run these in two terminals from the repo root:"
	@echo "  flask run"
	@echo "  cd frontend && npm run dev"
	@echo "Then open http://localhost:5173"

migrate:
	alembic -c backend/alembic.ini upgrade head
