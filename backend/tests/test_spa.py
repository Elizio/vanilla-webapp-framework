"""Tests for SPA static serving and fallback."""

import pytest


def _allow_methods(response):
    """Return the Allow header as a set of HTTP methods."""
    raw = response.headers.get('Allow') or ''
    return {part.strip() for part in raw.split(',') if part.strip()}


def test_spa_fallback_serves_index(production_client):
    response = production_client.get('/unknown-route')
    assert response.status_code == 200
    assert b'production' in response.data
    assert response.headers.get('Cache-Control') == 'no-cache'


@pytest.mark.parametrize('path', ['/login', '/dashboard'])
def test_spa_client_routes_serve_index(production_client, path):
    response = production_client.get(path)
    assert response.status_code == 200
    assert b'production' in response.data
    assert response.headers.get('Cache-Control') == 'no-cache'


def test_spa_serves_static_file(production_client):
    response = production_client.get('/file.txt')
    assert response.status_code == 200
    assert response.data == b'static-file'


def test_api_unknown_not_swallowed_by_spa(production_client):
    response = production_client.get('/api/unknown-endpoint')
    assert response.status_code == 404
    assert response.json == {'code': 'NOT_FOUND'}


@pytest.mark.parametrize('path', ['/api/login', '/api/register', '/api/logout'])
def test_get_on_post_only_api_route_returns_405(test_client, path):
    response = test_client.get(path)
    assert response.status_code == 405
    assert response.json == {'code': 'METHOD_NOT_ALLOWED'}
    assert 'POST' in _allow_methods(response)
