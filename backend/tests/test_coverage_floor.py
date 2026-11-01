"""Assert the backend coverage floor is configured and cannot be dropped."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"
SETUP_CFG = REPO_ROOT / "setup.cfg"

FAIL_UNDER_RE = re.compile(r"(?m)^fail_under\s*=\s*(\d+)\s*$")
PYTEST_INI_OPTIONS_RE = re.compile(
    r"(?m)^\[tool\.pytest\.ini_options\]\s*$",
)
PYTEST_SETUP_CFG_RE = re.compile(r"(?m)^\[tool:pytest\]\s*$")
MINIMUM_FLOOR = 80


def test_pyproject_declares_coverage_fail_under() -> None:
    """Coverage floor lives in pyproject.toml and omits backend tests."""
    text = PYPROJECT.read_text(encoding="utf-8")
    match = FAIL_UNDER_RE.search(text)
    assert match is not None, (
        "pyproject.toml must set [tool.coverage.report] fail_under so CI "
        "cannot silently drop the ratchet"
    )
    floor = int(match.group(1))
    assert floor >= MINIMUM_FLOOR, (
        f"fail_under={floor} is below {MINIMUM_FLOOR}; the ratchet is missing"
    )
    assert "backend/tests" in text, (
        "coverage omit must exclude backend/tests so the floor is on app code"
    )


def test_setup_cfg_pytest_is_not_shadowed_or_duplicated() -> None:
    """Keep pytest in setup.cfg unless it is moved wholesale to pyproject.toml.

    Adding [tool.pytest.ini_options] makes pytest ignore setup.cfg
    [tool:pytest]. Coverage fail_under must not be duplicated there.
    """
    pyproject = PYPROJECT.read_text(encoding="utf-8")
    setup_cfg = SETUP_CFG.read_text(encoding="utf-8")
    has_pytest_ini = PYTEST_INI_OPTIONS_RE.search(pyproject) is not None
    has_setup_pytest = PYTEST_SETUP_CFG_RE.search(setup_cfg) is not None
    assert has_pytest_ini ^ has_setup_pytest, (
        "pytest config must live in exactly one of pyproject.toml "
        "[tool.pytest.ini_options] or setup.cfg [tool:pytest]"
    )
    assert FAIL_UNDER_RE.search(setup_cfg) is None, (
        "fail_under must be configured in pyproject.toml only"
    )
