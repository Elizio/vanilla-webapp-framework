"""Prove Ruff, mypy, Biome and gitleaks fail on deliberately bad input.

Each test writes a tiny fixture in a temp directory (never in the repo)
and asserts the tool exits non-zero. Missing binaries skip locally;
Ruff and mypy are required when ``GITHUB_ACTIONS`` is set. Biome and
gitleaks are required in CI only when their well-known install paths
exist (frontend ``node_modules`` / ``.tools``), so the backend job can
skip them while the frontend and lint jobs still prove the failure.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
IN_CI = os.environ.get("GITHUB_ACTIONS") == "true"
BIOME_CANDIDATES = (REPO_ROOT / "frontend" / "node_modules" / ".bin" / "biome",)
GITLEAKS_CANDIDATES = (REPO_ROOT / ".tools" / "gitleaks",)


def _first_existing(paths: Sequence[Path]) -> str | None:
    """Return the first executable path, or None."""
    for path in paths:
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
    return None


def _require_tool(name: str, extra: Sequence[Path] = ()) -> str:
    """Return an executable path, skip locally, or fail when required in CI.

    Args:
        name: Binary name on ``PATH``.
        extra: Extra candidate paths (repo-local installs).

    Returns:
        Absolute path to the tool.

    Raises:
        pytest.skip.Exception: Tool is absent and not required here.
        AssertionError: Tool is required in this CI job but missing.
    """
    found = shutil.which(name) or _first_existing(extra)
    if found:
        return found
    required = IN_CI and name in {"ruff", "mypy"}
    if required:
        pytest.fail(f"{name} is required in CI but was not found on PATH")
    pytest.skip(f"{name} is not installed")


def _run(args: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run a command, capturing output, without raising."""
    return subprocess.run(
        list(args),
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )


def test_ruff_fails_on_unused_import(tmp_path: Path) -> None:
    """Ruff F401 must be a non-zero exit on a one-line unused import."""
    ruff = _require_tool("ruff")
    bad = tmp_path / "unused_import.py"
    bad.write_text("import os\n", encoding="utf-8")
    result = _run([ruff, "check", "--isolated", str(bad)], tmp_path)
    assert result.returncode != 0, result.stdout + result.stderr
    assert "F401" in result.stdout + result.stderr


def test_mypy_fails_on_type_error(tmp_path: Path) -> None:
    """mypy must reject a function whose body does not match its return type."""
    mypy = _require_tool("mypy")
    bad = tmp_path / "wrong_return.py"
    bad.write_text("def f(x: int) -> str:\n    return x\n", encoding="utf-8")
    config = tmp_path / "mypy.ini"
    config.write_text("[mypy]\n", encoding="utf-8")
    result = _run(
        [mypy, "--config-file", str(config), "--no-incremental", str(bad)],
        tmp_path,
    )
    assert result.returncode != 0, result.stdout + result.stderr


def test_biome_fails_on_debugger(tmp_path: Path) -> None:
    """Biome recommended rules must reject a ``debugger`` statement."""
    biome = _require_tool("biome", BIOME_CANDIDATES)
    bad = tmp_path / "debugger.js"
    bad.write_text("debugger;\n", encoding="utf-8")
    config = tmp_path / "biome.json"
    config.write_text(
        '{"linter":{"enabled":true,"rules":{"preset":"recommended"}}}\n',
        encoding="utf-8",
    )
    result = _run(
        [biome, "check", "--config-path", str(config), str(bad)],
        tmp_path,
    )
    assert result.returncode != 0, result.stdout + result.stderr


def test_gitleaks_fails_on_slack_token(tmp_path: Path) -> None:
    """gitleaks must flag a documented Slack bot-token pattern."""
    gitleaks = _require_tool("gitleaks", GITLEAKS_CANDIDATES)
    leak = tmp_path / "leak.txt"
    token = "-".join(
        ("xoxb", "123456789012", "1234567890123", "abcdefghijklmnopqrstuvwx")
    )
    leak.write_text(f"slack_token={token}\n", encoding="utf-8")
    result = _run(
        [gitleaks, "detect", "--no-git", "--source", str(tmp_path), "--verbose"],
        tmp_path,
    )
    assert result.returncode != 0, result.stdout + result.stderr
