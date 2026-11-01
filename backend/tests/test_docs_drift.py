"""Doc-drift sensor: env keys, DigitalOcean claims, and stale log paths."""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_EXAMPLE = REPO_ROOT / '.env.example'
README = REPO_ROOT / 'README.md'
MAKEFILE = REPO_ROOT / 'Makefile'
BACKEND_DIR = REPO_ROOT / 'backend'

# Keys that appear in one source on purpose. Each entry must stay justified.
#
# CODE_ONLY: read by backend Python but not an operator-facing .env key.
# DOCS_ONLY: documented for humans/frontend/build, not read via os.getenv
#            in backend application modules.
CODE_ONLY_ALLOWLIST = {
    'APP_VERSION',  # Bake-time Dockerfile ARG GIT_SHA / ENV APP_VERSION
    'API_HOST',  # Swagger host default; not required to start the app
}

DOCS_ONLY_ALLOWLIST = {
    'VITE_BASE_PATH',  # Vite build-time base; not read by backend Python
}

ENV_KEY_RE = re.compile(r'^[A-Z][A-Z0-9_]*$')
ENV_LINE_RE = re.compile(r'^#?\s*([A-Z][A-Z0-9_]+)=')
MAKE_TARGET_RE = re.compile(r'`make ([A-Za-z][A-Za-z0-9_-]*)`')
MAKEFILE_TARGET_RE = re.compile(r'^([A-Za-z][A-Za-z0-9_-]*):')
DIGITALOCEAN_RE = re.compile(r'digitalocean', re.IGNORECASE)
DATA_LOGS_RE = re.compile(r'/data/logs')

DOC_PATHS_FOR_DIGITALOCEAN = [
    README,
    REPO_ROOT / 'AGENTS.md',
    REPO_ROOT / 'backend' / 'AGENTS.md',
    REPO_ROOT / 'frontend' / 'AGENTS.md',
    *sorted((REPO_ROOT / '.cursor' / 'rules').glob('*.mdc')),
]

DOC_PATHS_FOR_DATA_LOGS = [
    README,
    REPO_ROOT / 'AGENTS.md',
    REPO_ROOT / 'backend' / 'AGENTS.md',
    REPO_ROOT / 'frontend' / 'AGENTS.md',
    ENV_EXAMPLE,
    *sorted((REPO_ROOT / '.cursor' / 'rules').glob('*.mdc')),
    *sorted(
        path
        for path in (REPO_ROOT / 'docs').rglob('*')
        if path.is_file()
        and path.suffix in {'.md', '.mdc', '.txt'}
        and 'superpowers' not in path.parts
    ),
]


def _iter_lines(path: Path) -> list[tuple[int, str]]:
    """Return 1-based (lineno, line) pairs without trailing newlines."""
    return list(enumerate(path.read_text(encoding='utf-8').splitlines(), start=1))


def parse_env_example_keys(path: Path) -> dict[str, list[int]]:
    """Parse ``KEY=`` and ``# KEY=`` assignments from ``.env.example``.

    Args:
        path: Path to ``.env.example``.

    Returns:
        Mapping of env key to the line numbers where it is assigned.
    """
    found: dict[str, list[int]] = {}
    for lineno, line in _iter_lines(path):
        match = ENV_LINE_RE.match(line)
        if not match:
            continue
        found.setdefault(match.group(1), []).append(lineno)
    return found


def parse_readme_env_table_keys(path: Path) -> dict[str, list[int]]:
    """Parse env keys from the README environment-variables table.

    Args:
        path: Path to ``README.md``.

    Returns:
        Mapping of env key to the table-row line numbers that mention it.
    """
    lines = _iter_lines(path)
    start = None
    for lineno, line in lines:
        stripped = line.strip()
        if stripped.startswith('| Variable |') and 'Description' in stripped:
            start = lineno
            break
    if start is None:
        return {}

    found: dict[str, list[int]] = {}
    for lineno, line in lines:
        if lineno <= start:
            continue
        stripped = line.strip()
        if not stripped.startswith('|'):
            break
        if re.match(r'^\|\s*-+', stripped):
            continue
        cells = [cell.strip() for cell in stripped.strip('|').split('|')]
        if not cells:
            continue
        for key in re.findall(r'`([A-Z][A-Z0-9_]+)`', cells[0]):
            if ENV_KEY_RE.fullmatch(key):
                found.setdefault(key, []).append(lineno)
    return found


def _env_keys_from_ast(tree: ast.AST) -> set[str]:
    """Collect ``os.getenv`` / ``os.environ`` string keys from a module AST."""
    keys: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = None
        if isinstance(func, ast.Attribute) and func.attr in {'getenv', 'get'}:
            if isinstance(func.value, ast.Attribute) and func.value.attr == 'environ':
                name = 'environ.get'
            elif isinstance(func.value, ast.Name) and func.value.id == 'os':
                name = func.attr
            elif (
                isinstance(func.value, ast.Name)
                and func.value.id == 'environ'
            ):
                name = 'environ.get'
        if name is None:
            continue
        if not node.args:
            continue
        first = node.args[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            if ENV_KEY_RE.fullmatch(first.value):
                keys.add(first.value)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Subscript):
            continue
        target = node.value
        is_environ = (
            (isinstance(target, ast.Attribute) and target.attr == 'environ')
            or (isinstance(target, ast.Name) and target.id == 'environ')
        )
        if not is_environ:
            continue
        sl = node.slice
        if isinstance(sl, ast.Constant) and isinstance(sl.value, str):
            if ENV_KEY_RE.fullmatch(sl.value):
                keys.add(sl.value)
    return keys


def parse_backend_env_keys() -> dict[str, list[str]]:
    """Collect env keys read by backend application modules.

    Scans ``backend/config/*.py`` and every other ``backend/**/*.py``
    module except ``backend/tests``.

    Returns:
        Mapping of env key to the relative file paths that read it.
    """
    found: dict[str, list[str]] = {}
    for path in sorted(BACKEND_DIR.rglob('*.py')):
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel.startswith('backend/tests/'):
            continue
        tree = ast.parse(path.read_text(encoding='utf-8'), filename=rel)
        for key in _env_keys_from_ast(tree):
            found.setdefault(key, []).append(rel)
    return found


def parse_make_mentions(paths: list[Path]) -> dict[str, list[str]]:
    """Collect ``make <target>`` mentions from docs.

    Args:
        paths: Markdown files to scan.

    Returns:
        Mapping of make target to ``file:line`` locations.
    """
    found: dict[str, list[str]] = {}
    for path in paths:
        for lineno, line in _iter_lines(path):
            for target in MAKE_TARGET_RE.findall(line):
                loc = f'{path.relative_to(REPO_ROOT).as_posix()}:{lineno}'
                found.setdefault(target, []).append(loc)
    return found


def parse_makefile_targets(path: Path) -> set[str]:
    """Return explicit targets declared in ``Makefile``."""
    targets: set[str] = set()
    for _, line in _iter_lines(path):
        if line.startswith('.PHONY:'):
            targets.update(line.split(':', 1)[1].split())
            continue
        match = MAKEFILE_TARGET_RE.match(line)
        if match:
            targets.add(match.group(1))
    return targets


def _format_locations(path: Path, linenos: list[int]) -> str:
    rel = path.relative_to(REPO_ROOT).as_posix()
    return ', '.join(f'{rel}:{n}' for n in linenos)


def test_readme_env_table_matches_env_example():
    """README env-table keys must match ``KEY=`` / ``# KEY=`` in ``.env.example``."""
    example = parse_env_example_keys(ENV_EXAMPLE)
    readme = parse_readme_env_table_keys(README)
    extra_readme = sorted(set(readme) - set(example))
    missing_readme = sorted(set(example) - set(readme))
    errors = []
    for key in extra_readme:
        errors.append(
            f'stale README env key {key} at '
            f'{_format_locations(README, readme[key])} '
            '(not in .env.example)'
        )
    for key in missing_readme:
        errors.append(
            f'undocumented env key {key} at '
            f'{_format_locations(ENV_EXAMPLE, example[key])} '
            '(missing from README env table)'
        )
    assert not errors, 'Env-key drift:\n' + '\n'.join(errors)


def test_backend_env_keys_are_documented():
    """Backend getenv/environ names must be documented or allowlisted."""
    example = set(parse_env_example_keys(ENV_EXAMPLE))
    readme = set(parse_readme_env_table_keys(README))
    documented = example | readme
    code = parse_backend_env_keys()

    undocumented = sorted(set(code) - documented - CODE_ONLY_ALLOWLIST)
    stale_docs = sorted(
        documented - set(code) - DOCS_ONLY_ALLOWLIST
    )
    errors = []
    for key in undocumented:
        files = ', '.join(code[key])
        errors.append(f'undocumented env key {key} read in {files}')
    for key in stale_docs:
        errors.append(
            f'stale documented env key {key} is not read by backend application code'
        )
    unused_code_allow = sorted(CODE_ONLY_ALLOWLIST - set(code))
    unused_docs_allow = sorted(DOCS_ONLY_ALLOWLIST - documented)
    for key in unused_code_allow:
        errors.append(f'CODE_ONLY_ALLOWLIST entry {key} is not read by backend code')
    for key in unused_docs_allow:
        errors.append(f'DOCS_ONLY_ALLOWLIST entry {key} is not documented')
    assert not errors, 'Env-key drift:\n' + '\n'.join(errors)


def test_no_digitalocean_deploy_claims_in_agent_docs():
    """README, AGENTS, and Cursor rules must not claim a DigitalOcean deploy.

    Historical notes under ``docs/superpowers/`` and the unused
    ``.github/workflows/deploy.yml`` stub are excluded.
    """
    hits = []
    for path in DOC_PATHS_FOR_DIGITALOCEAN:
        for lineno, line in _iter_lines(path):
            if DIGITALOCEAN_RE.search(line):
                rel = path.relative_to(REPO_ROOT).as_posix()
                hits.append(f'{rel}:{lineno}: {line.strip()}')
    assert not hits, 'DigitalOcean deploy claim:\n' + '\n'.join(hits)


def test_no_data_logs_paths_in_docs():
    """Operator docs must not mention the retired ``/data/logs`` log directory."""
    hits = []
    for path in DOC_PATHS_FOR_DATA_LOGS:
        for lineno, line in _iter_lines(path):
            if DATA_LOGS_RE.search(line):
                rel = path.relative_to(REPO_ROOT).as_posix()
                hits.append(f'{rel}:{lineno}: {line.strip()}')
    assert not hits, 'Stale /data/logs path:\n' + '\n'.join(hits)


def test_make_targets_mentioned_in_docs_exist():
    """Every ``make <target>`` in README/AGENTS must exist once a Makefile does."""
    if not MAKEFILE.is_file():
        pytest.skip('Makefile not present yet (#13 Phase 1)')
    declared = parse_makefile_targets(MAKEFILE)
    mentions = parse_make_mentions(
        [
            README,
            REPO_ROOT / 'AGENTS.md',
            REPO_ROOT / 'backend' / 'AGENTS.md',
            REPO_ROOT / 'frontend' / 'AGENTS.md',
        ]
    )
    missing = {
        target: locs
        for target, locs in mentions.items()
        if target not in declared
    }
    errors = [
        f'make {target} mentioned at {", ".join(locs)} is not in Makefile'
        for target, locs in sorted(missing.items())
    ]
    assert not errors, 'Unknown make targets:\n' + '\n'.join(errors)
