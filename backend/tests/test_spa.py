"""Tests for SPA static serving and fallback."""


def test_spa_fallback_serves_index(production_client):
    response = production_client.get('/unknown-route')
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
