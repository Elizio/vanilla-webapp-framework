"""Behaviour tests for the migrate-once container entrypoint."""
import os
import stat
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ENTRYPOINT = REPO_ROOT / 'docker-entrypoint.sh'


def _fake_bin(tmp_path, alembic_script, gunicorn_script='#!/bin/sh\nexit 0\n'):
    """Create a PATH overlay with stub alembic and gunicorn executables."""
    bindir = tmp_path / 'bin'
    bindir.mkdir()
    for name, body in (('alembic', alembic_script), ('gunicorn', gunicorn_script)):
        path = bindir / name
        path.write_text(body)
        path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return bindir


def _run(tmp_path, env, args=None, alembic='#!/bin/sh\nexit 0\n', gunicorn=None):
    """Run the entrypoint with a controlled PATH and environment."""
    if gunicorn is None:
        gunicorn = f'#!/bin/sh\necho gunicorn >> "{tmp_path / "gunicorn.ran"}"\n'
    bindir = _fake_bin(tmp_path, alembic, gunicorn)
    run_env = {
        'PATH': f'{bindir}:{os.environ.get("PATH", "")}',
        'HOME': str(tmp_path),
    }
    run_env.update(env)
    return subprocess.run(
        ['/bin/sh', str(ENTRYPOINT), *(args or [])],
        cwd=str(tmp_path),
        env=run_env,
        capture_output=True,
        text=True,
        check=False,
    )


def _required_env():
    return {
        'FLASK_SECRET': 'entrypoint-secret-value-must-not-leak',
        'JWT_SECRET': 'entrypoint-jwt-value-must-not-leak',
        'DATABASE_URI': 'sqlite:////tmp/secret-db-path-must-not-leak.db',
    }


def test_entrypoint_script_exists_and_is_executable():
    """The image entrypoint lives at the repo root and is executable."""
    assert ENTRYPOINT.is_file()
    assert os.access(ENTRYPOINT, os.X_OK)


def test_entrypoint_errors_on_missing_required_env_without_echoing_values(tmp_path):
    """Missing JWT_SECRET fails fast, names the var, and never prints other secrets."""
    env = _required_env()
    del env['JWT_SECRET']
    result = _run(tmp_path, env, args=['gunicorn'])
    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert 'JWT_SECRET' in result.stderr
    assert 'entrypoint-secret-value-must-not-leak' not in combined
    assert 'secret-db-path-must-not-leak' not in combined


def test_entrypoint_errors_on_missing_flask_secret(tmp_path):
    """FLASK_SECRET is required and the value is never echoed."""
    env = _required_env()
    secret = env.pop('FLASK_SECRET')
    result = _run(tmp_path, env, args=['gunicorn'])
    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert 'FLASK_SECRET' in result.stderr
    assert secret not in combined


def test_entrypoint_errors_on_missing_database_uri(tmp_path):
    """DATABASE_URI is required and the value is never echoed."""
    env = _required_env()
    uri = env.pop('DATABASE_URI')
    result = _run(tmp_path, env, args=['gunicorn'])
    combined = result.stdout + result.stderr
    assert result.returncode != 0
    assert 'DATABASE_URI' in result.stderr
    assert uri not in combined


def test_entrypoint_logs_running_migrations_once_then_execs(tmp_path):
    """The entrypoint prints Running migrations exactly once, then execs gunicorn."""
    trace = tmp_path / 'trace.txt'
    alembic = (
        '#!/bin/sh\n'
        f'echo alembic "$@" >> "{trace}"\n'
    )
    gunicorn = (
        '#!/bin/sh\n'
        f'echo gunicorn >> "{trace}"\n'
    )
    result = _run(
        tmp_path,
        _required_env(),
        args=['gunicorn', '--bind', '0.0.0.0:5000'],
        alembic=alembic,
        gunicorn=gunicorn,
    )
    assert result.returncode == 0
    assert result.stdout.count('Running migrations') == 1
    assert 'Booting worker' not in result.stdout
    assert 'entrypoint-secret-value-must-not-leak' not in result.stdout + result.stderr
    assert 'alembic -c backend/alembic.ini upgrade head' in trace.read_text()
    assert 'gunicorn' in trace.read_text()


def test_entrypoint_fails_fast_when_migration_fails(tmp_path):
    """A failed alembic upgrade must not start gunicorn."""
    gunicorn_ran = tmp_path / 'gunicorn.ran'
    result = _run(
        tmp_path,
        _required_env(),
        args=['gunicorn'],
        alembic='#!/bin/sh\nexit 3\n',
        gunicorn=f'#!/bin/sh\necho ran >> "{gunicorn_ran}"\n',
    )
    assert result.returncode != 0
    assert not gunicorn_ran.exists()
    assert 'Running migrations' in result.stdout


def test_entrypoint_gunicorn_has_no_access_logfile(tmp_path):
    """Access logs would record OAuth ?code= and token query strings in docker logs."""
    trace = tmp_path / 'gunicorn.args'
    gunicorn = (
        '#!/bin/sh\n'
        f'printf "%s\\n" "$*" > "{trace}"\n'
    )
    result = _run(
        tmp_path,
        _required_env(),
        args=['gunicorn'],
        gunicorn=gunicorn,
    )
    assert result.returncode == 0
    args = trace.read_text()
    assert '--access-logfile' not in args
    assert '--error-logfile' in args
    assert '--access-logfile' not in ENTRYPOINT.read_text()


def test_entrypoint_skips_migrate_for_non_server_commands(tmp_path):
    """Diagnostic commands (id, true) must not require secrets or run alembic."""
    trace = tmp_path / 'alembic.ran'
    result = _run(
        tmp_path,
        {},
        args=['true'],
        alembic=f'#!/bin/sh\necho ran >> "{trace}"\n',
    )
    assert result.returncode == 0
    assert not trace.exists()
    assert 'Running migrations' not in result.stdout
