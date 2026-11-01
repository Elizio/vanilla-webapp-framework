"""CI workflow steps stay aligned with Makefile targets.

``make check`` is the local equivalent of CI. This module parses the
Makefile and ``.github/workflows/*.yml`` so a new CI gate cannot land
without a matching make target (and the other way around).
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MAKEFILE = REPO_ROOT / "Makefile"
CI_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ci.yml"
DOCKER_PUBLISH = REPO_ROOT / ".github" / "workflows" / "docker-publish.yml"

MAKE_RUN_RE = re.compile(r"(?m)^\s*(?:-\s+)?run:\s*make\s+(.+?)\s*$")
MAKEFILE_TARGET_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):(?:\s*(.*))?$")

# Gates that must appear as ``run: make <target>`` in ci.yml, and must
# be in the recursive prerequisite closure of ``make check``.
CI_CHECK_TARGETS = (
    "check-pins",
    "audit-python",
    "lint-python",
    "prove-ruff-fail",
    "prove-mypy-fail",
    "migrations-check",
    "test-backend",
    "audit-frontend",
    "lint-frontend",
    "prove-biome-fail",
    "build-frontend",
    "test-frontend",
    "lint-shell",
    "prove-gitleaks-fail",
)

# Smoke needs Docker and is not part of ``make check``.
CI_SMOKE_TARGET = "smoke"

# Raw commands that used to live in CI and must not return.
FORBIDDEN_CI_RUNS = (
    re.compile(r"(?m)^\s*run:\s*pytest\s*$"),
    re.compile(r"(?m)^\s*run:\s*pip-audit\b"),
    re.compile(r"(?m)^\s*run:\s*python\s+scripts/check_pins\.py\s*$"),
    re.compile(r"(?m)^\s*run:\s*cd frontend && npm audit\b"),
    re.compile(r"(?m)^\s*run:\s*cd frontend && npm run build\s*$"),
    re.compile(r"(?m)^\s*run:\s*cd frontend && npm run test"),
    re.compile(r"(?m)^\s*run:\s*test -f backend/static/index\.html\s*$"),
)

DEPENDABOT = REPO_ROOT / ".github" / "dependabot.yml"


def parse_makefile_prereqs(path: Path) -> dict[str, list[str]]:
    """Return ``target -> prerequisite names`` from a Makefile."""
    prereqs: dict[str, list[str]] = {}
    pending_target: str | None = None
    pending_prereqs: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith(".PHONY:"):
            continue
        if raw.startswith("\t"):
            continue
        if raw.endswith("\\"):
            body = raw[:-1].strip()
            if pending_target is None:
                match = MAKEFILE_TARGET_RE.match(body)
                if match:
                    pending_target = match.group(1)
                    pending_prereqs = (match.group(2) or "").split()
            else:
                pending_prereqs.extend(body.split())
            continue
        if pending_target is not None:
            pending_prereqs.extend(raw.split())
            prereqs[pending_target] = pending_prereqs
            pending_target = None
            pending_prereqs = []
            continue
        match = MAKEFILE_TARGET_RE.match(raw)
        if match:
            prereqs[match.group(1)] = (match.group(2) or "").split()
    return prereqs


def closure(prereqs: dict[str, list[str]], start: str) -> set[str]:
    """Return ``start`` plus every recursive Makefile prerequisite."""
    seen: set[str] = set()
    stack = [start]
    while stack:
        name = stack.pop()
        if name in seen:
            continue
        seen.add(name)
        stack.extend(prereqs.get(name, []))
    return seen


def make_targets_in_workflow(path: Path) -> set[str]:
    """Return ``make <target>`` names invoked via a workflow ``run:`` step."""
    found: set[str] = set()
    for group in MAKE_RUN_RE.findall(path.read_text(encoding="utf-8")):
        for name in group.split():
            if name.startswith("-"):
                continue
            found.add(name)
    return found


def test_ci_invokes_make_targets_that_exist() -> None:
    """Every ``run: make X`` in CI / docker-publish is a real Makefile target."""
    declared = set(parse_makefile_prereqs(MAKEFILE))
    invoked = make_targets_in_workflow(CI_WORKFLOW) | make_targets_in_workflow(
        DOCKER_PUBLISH
    )
    missing = sorted(invoked - declared)
    assert invoked, "CI workflows must call make targets"
    assert not missing, "Unknown make targets in workflows: " + ", ".join(missing)


def test_make_check_covers_ci_gates() -> None:
    """``make check`` recursively includes every CI gate except Docker smoke."""
    prereqs = parse_makefile_prereqs(MAKEFILE)
    covered = closure(prereqs, "check")
    missing = [name for name in CI_CHECK_TARGETS if name not in covered]
    assert "check" in prereqs, "Makefile must declare a check target"
    assert not missing, (
        "make check is missing CI gates (add them as prerequisites): "
        + ", ".join(missing)
    )
    assert CI_SMOKE_TARGET not in covered, (
        "make smoke stays out of make check (Docker-only, slow)"
    )


def test_ci_jobs_call_expected_make_targets() -> None:
    """ci.yml backend/frontend/lint jobs call the shared make targets."""
    ci_targets = make_targets_in_workflow(CI_WORKFLOW)
    missing = [name for name in CI_CHECK_TARGETS if name not in ci_targets]
    assert not missing, "ci.yml is missing make targets: " + ", ".join(missing)


def test_ci_does_not_use_raw_commands_that_drift_from_make() -> None:
    """CI must not re-introduce the pre-Phase-2 raw commands."""
    text = CI_WORKFLOW.read_text(encoding="utf-8")
    hits = [pattern.pattern for pattern in FORBIDDEN_CI_RUNS if pattern.search(text)]
    assert not hits, "ci.yml still has raw commands: " + "; ".join(hits)


def test_docker_publish_smokes_via_make() -> None:
    """The image that will be published is smoke-tested with ``make smoke``."""
    targets = make_targets_in_workflow(DOCKER_PUBLISH)
    assert CI_SMOKE_TARGET in targets


def test_migrations_check_script_round_trips() -> None:
    """``scripts/migrations-check.sh`` upgrades, checks, downgrades, upgrades."""
    script = REPO_ROOT / "scripts" / "migrations-check.sh"
    assert script.is_file(), "scripts/migrations-check.sh is required"
    result = subprocess.run(
        [str(script)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_smoke_script_requires_image() -> None:
    """``scripts/smoke-image.sh`` exits non-zero when IMAGE is unset."""
    script = REPO_ROOT / "scripts" / "smoke-image.sh"
    assert script.is_file(), "scripts/smoke-image.sh is required"
    result = subprocess.run(
        [str(script)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "IMAGE": ""},
    )
    # Empty IMAGE should still fail the :? check.
    assert result.returncode != 0


def test_dependabot_ignores_python_minor_and_node_major() -> None:
    """Python 3.10→3.15 must not be a Dependabot minor bump (see PR #24)."""
    text = DEPENDABOT.read_text(encoding="utf-8")
    assert "flake8" not in text
    assert "black" not in text
    assert "dependency-name: \"python\"" in text or "dependency-name: 'python'" in text
    assert "dependency-name: \"node\"" in text or "dependency-name: 'node'" in text
    assert "version-update:semver-minor" in text
    assert "version-update:semver-major" in text
