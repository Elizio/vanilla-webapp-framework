"""APP_BASE_PATH normalization and rejection."""

import pytest

from backend.config.app_config import reset_app_config_for_tests


def _reload_config(monkeypatch, **env):
    """Rebuild AppConfig after applying env overrides.

    Args:
        monkeypatch: pytest monkeypatch fixture.
        **env: Environment variables to set. ``None`` deletes the key.
    """
    for key, value in env.items():
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)
    monkeypatch.setenv('APP_PROFILE', env.get('APP_PROFILE', 'testing'))
    reset_app_config_for_tests()
    from backend.config.app_config import AppConfig

    return AppConfig.get_instance()


@pytest.fixture(autouse=True)
def _restore_config(monkeypatch):
    """Reset AppConfig after each test so later fixtures see defaults."""
    yield
    monkeypatch.setenv('APP_PROFILE', 'testing')
    monkeypatch.delenv('APP_BASE_PATH', raising=False)
    reset_app_config_for_tests()


def test_app_base_path_unset_is_slash(monkeypatch):
    """Empty or missing APP_BASE_PATH normalizes to ``/``."""
    config = _reload_config(monkeypatch, APP_BASE_PATH=None)
    assert config.APP_BASE_PATH == '/'

    config = _reload_config(monkeypatch, APP_BASE_PATH='')
    assert config.APP_BASE_PATH == '/'

    config = _reload_config(monkeypatch, APP_BASE_PATH='   ')
    assert config.APP_BASE_PATH == '/'


def test_app_base_path_adds_leading_slash_and_strips_trailing(monkeypatch):
    """A bare or trailing-slash value becomes a single leading-slash path."""
    config = _reload_config(monkeypatch, APP_BASE_PATH='vanilla-webapp-framework/')
    assert config.APP_BASE_PATH == '/vanilla-webapp-framework'

    config = _reload_config(monkeypatch, APP_BASE_PATH='/vanilla-webapp-framework/')
    assert config.APP_BASE_PATH == '/vanilla-webapp-framework'


def test_app_base_path_root_stays_slash(monkeypatch):
    """A lone slash stays ``/`` rather than becoming empty."""
    config = _reload_config(monkeypatch, APP_BASE_PATH='/')
    assert config.APP_BASE_PATH == '/'


def test_app_base_path_sets_session_cookie_path(monkeypatch):
    """Flask session cookie path follows APP_BASE_PATH."""
    config = _reload_config(monkeypatch, APP_BASE_PATH='/vanilla-webapp-framework')
    assert config.SESSION_COOKIE_PATH == '/vanilla-webapp-framework'

    config = _reload_config(monkeypatch, APP_BASE_PATH=None)
    assert config.SESSION_COOKIE_PATH == '/'


@pytest.mark.parametrize(
    'raw',
    [
        'https://dsfor.fun/vanilla-webapp-framework',
        'http://example.com/app',
        '//dsfor.fun/app',
        '/app?next=1',
        '/foo/../bar',
        '/foo/..',
    ],
)
def test_app_base_path_rejects_url_like_or_dotdot(monkeypatch, raw):
    """Scheme, host, query, and ``..`` are rejected without echoing secrets."""
    monkeypatch.setenv('APP_BASE_PATH', raw)
    monkeypatch.setenv('APP_PROFILE', 'testing')
    with pytest.raises(ValueError, match='APP_BASE_PATH') as exc_info:
        reset_app_config_for_tests()
    message = str(exc_info.value)
    assert 'FLASK_SECRET' not in message
    assert 'JWT_SECRET' not in message
    assert raw not in message
