"""Tests for scripts/init-project and the placeholder list."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "init-project"
PLACEHOLDERS = REPO_ROOT / "docs" / "template-placeholders.md"
MAKEFILE = REPO_ROOT / "Makefile"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "template-init.yml"

REQUIRED_KEYS = (
    "PROJECT_SLUG",
    "PROJECT_TITLE",
    "FRONTEND_PACKAGE",
    "IMAGE_NAME",
    "PUBLIC_HOST",
    "APP_SUBPATH",
    "HOSTINGER_VM",
    "HOSTINGER_PROJECT",
    "GITHUB_OWNER",
    "SETUP_AUTHOR",
    "SETUP_EMAIL",
    "SETUP_URL",
)

def _run_init(root: Path, name: str, *extra: str) -> subprocess.CompletedProcess[str]:
    """Run init-project against ``root``."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--name", name, "--root", str(root), *extra],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )


def test_placeholders_doc_lists_every_key() -> None:
    """The placeholders file is the single source of template names."""
    text = PLACEHOLDERS.read_text(encoding="utf-8")
    for key in REQUIRED_KEYS:
        assert f"{key}=" in text, f"missing {key} in {PLACEHOLDERS}"
    assert "vanilla-webapp-framework" in text
    assert "dsfor.fun" in text
    assert "1136636" in text


def test_makefile_has_init_target() -> None:
    """``make init NAME=...`` is wired to the script."""
    text = MAKEFILE.read_text(encoding="utf-8")
    assert "init:" in text
    assert "scripts/init-project" in text


def test_template_init_workflow_is_non_required() -> None:
    """A separate workflow runs init; it must not reuse required job names."""
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "template-init:" in text
    assert "permissions:\n  contents: read" in text
    forbidden = (
        "packages: write",
        "\n  backend:",
        "\n  frontend:",
        "\n  deploy:",
    )
    for name in forbidden:
        assert name not in text
    assert "actions/checkout@11d5960a326750d5838078e36cf38b85af677262" in text


def test_init_rejects_invalid_name(tmp_path: Path) -> None:
    """Slugs must be lowercase kebab-case."""
    dest = tmp_path / "copy"
    dest.mkdir()
    result = _run_init(dest, "Demo App", "--skip-check")
    assert result.returncode == 2
    assert "NAME must match" in result.stderr


def test_init_rewrites_copy_and_clears_template_names(tmp_path: Path) -> None:
    """A throwaway copy named demoapp has no leftover template strings."""
    dest = tmp_path / "copy"
    dest.mkdir()
    (dest / "docs").mkdir()
    shutil.copy(PLACEHOLDERS, dest / "docs" / "template-placeholders.md")
    (dest / "setup.py").write_text(
        REPO_ROOT.joinpath("setup.py").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (dest / "README.md").write_text(
        "Vanilla WebApp Framework\n"
        "ghcr.io/elizio/vanilla-webapp-framework\n"
        "https://dsfor.fun/vanilla-webapp-framework\n"
        "VM 1136636 project dsfor\n"
        "frontend package vanilla-webapp-frontend\n",
        encoding="utf-8",
    )
    plans = dest / "docs" / "superpowers" / "plans"
    specs = dest / "docs" / "superpowers" / "specs"
    plans.mkdir(parents=True)
    specs.mkdir(parents=True)
    (plans / "old.md").write_text("historical plan\n", encoding="utf-8")
    (specs / "old.md").write_text("historical spec\n", encoding="utf-8")
    stray = dest / "vibe-prompts-examples"
    stray.mkdir()
    (stray / "temp.txt").write_text("scratch\n", encoding="utf-8")
    result = _run_init(dest, "demoapp", "--skip-check")
    assert result.returncode == 0, result.stdout + result.stderr

    leftovers = (
        "vanilla-webapp-framework",
        "Vanilla WebApp Framework",
        "vanilla-webapp-frontend",
        "dsfor.fun",
        "1136636",
        "elizio/vanilla-webapp-framework",
    )
    hits: list[str] = []
    for path in dest.rglob("*"):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for needle in leftovers:
            if needle in text:
                hits.append(f"{path.relative_to(dest)}:{needle}")
                break
    assert not hits, "leftover template names:\n" + "\n".join(hits[:30])

    new_placeholders = (dest / "docs" / "template-placeholders.md").read_text(
        encoding="utf-8"
    )
    assert "PROJECT_SLUG=demoapp" in new_placeholders
    assert "PUBLIC_HOST=example.test" in new_placeholders
    setup = (dest / "setup.py").read_text(encoding="utf-8")
    assert "demoapp" in setup
    assert "Your Name" not in setup
    assert not (dest / "vibe-prompts-examples" / "temp.txt").exists()
    assert (dest / "docs" / "superpowers" / "README.md").is_file()
    assert not (dest / "docs" / "superpowers" / "plans").exists()
