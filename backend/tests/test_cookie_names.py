"""Namespaced cookie names derived from COOKIE_PREFIX / APP_NAME."""

from __future__ import annotations

import pytest

from backend.config.app_config import AppConfig, reset_app_config_for_tests
from backend.config.cookie_names import (
    DEFAULT_COOKIE_PREFIX,
    cookie_name_prefix,
    namespaced_cookie_name,
    resolve_cookie_name,
    resolve_cookie_prefix,
)


def test_cookie_name_prefix_uses_default_when_unset() -> None:
    """Unset or blank APP_NAME must not produce a leading underscore."""
    assert cookie_name_prefix(None) == DEFAULT_COOKIE_PREFIX
    assert cookie_name_prefix('') == DEFAULT_COOKIE_PREFIX
    assert cookie_name_prefix('   ') == DEFAULT_COOKIE_PREFIX
    assert cookie_name_prefix('!!!') == DEFAULT_COOKIE_PREFIX
    assert not cookie_name_prefix(None).startswith('_')
    assert not cookie_name_prefix(None).startswith('-')


def test_cookie_name_prefix_slugs_display_names() -> None:
    """Human APP_NAME values become a stable hyphenated slug."""
    assert cookie_name_prefix('Garage Boss') == 'garage-boss'
    assert cookie_name_prefix('garage-boss') == 'garage-boss'
    assert cookie_name_prefix('Vanilla WebApp Framework') == (
        'vanilla-webapp-framework'
    )
    assert cookie_name_prefix('_hidden_app_') == 'hidden-app'


def test_namespaced_cookie_name_appends_legacy_suffix() -> None:
    """Live cookie names are the prefix plus the legacy suffix."""
    assert namespaced_cookie_name('garage-boss', 'csrf_token') == (
        'garage-boss_csrf_token'
    )
    assert namespaced_cookie_name(DEFAULT_COOKIE_PREFIX, 'auth_token') == (
        f'{DEFAULT_COOKIE_PREFIX}_auth_token'
    )


def test_resolve_cookie_prefix_prefers_cookie_prefix_over_app_name() -> None:
    """COOKIE_PREFIX wins; otherwise the slug of APP_NAME is used."""
    assert resolve_cookie_prefix('gb', 'vanilla-webapp-framework') == 'gb'
    assert resolve_cookie_prefix('Garage Boss', 'other') == 'garage-boss'
    assert resolve_cookie_prefix(None, 'garage-boss') == 'garage-boss'
    assert resolve_cookie_prefix('', None) == DEFAULT_COOKIE_PREFIX
    assert resolve_cookie_prefix('   ', '!!!') == DEFAULT_COOKIE_PREFIX


def test_resolve_cookie_name_honors_non_empty_override() -> None:
    """Explicit CSRF_COOKIE_NAME (and siblings) win over the prefix."""
    assert (
        resolve_cookie_name('custom_csrf', 'garage-boss', 'csrf_token') == 'custom_csrf'
    )
    assert resolve_cookie_name('  ', 'garage-boss', 'csrf_token') == (
        'garage-boss_csrf_token'
    )
    assert resolve_cookie_name(None, DEFAULT_COOKIE_PREFIX, 'csrf_token') == (
        f'{DEFAULT_COOKIE_PREFIX}_csrf_token'
    )


def _reload_config(monkeypatch: pytest.MonkeyPatch, **env: str | None) -> AppConfig:
    """Rebuild AppConfig after applying env overrides."""
    for key, value in env.items():
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)
    profile = env.get('APP_PROFILE') or 'testing'
    monkeypatch.setenv('APP_PROFILE', profile)
    reset_app_config_for_tests()
    return AppConfig.get_instance()


def test_app_config_namespaces_cookies_from_app_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """APP_NAME slugs every session cookie when COOKIE_PREFIX is unset."""
    config = _reload_config(monkeypatch, APP_NAME='garage-boss')
    try:
        assert config.COOKIE_PREFIX == 'garage-boss'
        assert config.CSRF_COOKIE_NAME == 'garage-boss_csrf_token'
        assert config.AUTH_COOKIE_NAME == 'garage-boss_auth_token'
        assert config.REFRESH_COOKIE_NAME == 'garage-boss_refresh_token'
        assert config.AUTH_DEVICE_COOKIE_NAME == 'garage-boss_auth_device'
    finally:
        monkeypatch.delenv('APP_NAME', raising=False)
        reset_app_config_for_tests()


def test_app_config_namespaces_cookies_without_app_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing APP_NAME still uses the deterministic default prefix."""
    config = _reload_config(monkeypatch, APP_NAME=None)
    try:
        prefix = DEFAULT_COOKIE_PREFIX
        assert config.COOKIE_PREFIX == prefix
        assert config.CSRF_COOKIE_NAME == f'{prefix}_csrf_token'
        assert config.AUTH_COOKIE_NAME == f'{prefix}_auth_token'
        assert config.REFRESH_COOKIE_NAME == f'{prefix}_refresh_token'
        assert config.AUTH_DEVICE_COOKIE_NAME == f'{prefix}_auth_device'
    finally:
        reset_app_config_for_tests()


def test_app_config_cookie_prefix_overrides_app_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """COOKIE_PREFIX namespaces cookies independently of APP_NAME."""
    config = _reload_config(
        monkeypatch, APP_NAME='vanilla-webapp-framework', COOKIE_PREFIX='gb'
    )
    try:
        assert config.COOKIE_PREFIX == 'gb'
        assert config.CSRF_COOKIE_NAME == 'gb_csrf_token'
        assert config.AUTH_COOKIE_NAME == 'gb_auth_token'
        assert config.REFRESH_COOKIE_NAME == 'gb_refresh_token'
        assert config.AUTH_DEVICE_COOKIE_NAME == 'gb_auth_device'
    finally:
        monkeypatch.delenv('APP_NAME', raising=False)
        monkeypatch.delenv('COOKIE_PREFIX', raising=False)
        reset_app_config_for_tests()


def test_app_config_cookie_name_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Per-cookie env vars replace the namespaced defaults."""
    config = _reload_config(
        monkeypatch,
        APP_NAME='garage-boss',
        CSRF_COOKIE_NAME='gb_csrf',
        AUTH_COOKIE_NAME='gb_auth',
        REFRESH_COOKIE_NAME='gb_refresh',
        AUTH_DEVICE_COOKIE_NAME='gb_device',
    )
    try:
        assert config.CSRF_COOKIE_NAME == 'gb_csrf'
        assert config.AUTH_COOKIE_NAME == 'gb_auth'
        assert config.REFRESH_COOKIE_NAME == 'gb_refresh'
        assert config.AUTH_DEVICE_COOKIE_NAME == 'gb_device'
    finally:
        for key in (
            'APP_NAME',
            'CSRF_COOKIE_NAME',
            'AUTH_COOKIE_NAME',
            'REFRESH_COOKIE_NAME',
            'AUTH_DEVICE_COOKIE_NAME',
        ):
            monkeypatch.delenv(key, raising=False)
        reset_app_config_for_tests()
