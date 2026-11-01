"""Static checks on the production Dockerfile."""
from pathlib import Path

DOCKERFILE = Path(__file__).resolve().parents[2] / 'Dockerfile'


def test_dockerfile_runs_as_uid_10001():
    """The runtime user is UID/GID 10001; no gosu or root entrypoint."""
    text = DOCKERFILE.read_text()
    assert 'USER 10001:10001' in text
    assert 'useradd' in text and '10001' in text
    assert 'gosu' not in text
    assert 'USER root' not in text
    assert 'chown -R app:app /app' not in text
    assert 'chown -R app:app /app/backend/static' not in text


def test_dockerfile_healthcheck_uses_urllib_not_curl():
    """HEALTHCHECK must use the stdlib urllib helper, not curl."""
    text = DOCKERFILE.read_text()
    assert 'HEALTHCHECK' in text
    assert 'container_healthcheck.py' in text
    health_lines = [
        line
        for line in text.splitlines()
        if 'HEALTHCHECK' in line or 'container_healthcheck' in line
    ]
    assert health_lines
    assert all('curl' not in line.lower() for line in health_lines)


def test_dockerfile_bakes_app_version_last():
    """ARG GIT_SHA / ENV APP_VERSION stay last so earlier layers cache."""
    lines = [
        line.strip()
        for line in DOCKERFILE.read_text().splitlines()
        if line.strip() and not line.strip().startswith('#')
    ]
    assert lines[-2].startswith('ARG GIT_SHA')
    assert lines[-1].startswith('ENV APP_VERSION')
