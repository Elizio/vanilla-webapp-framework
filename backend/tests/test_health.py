"""Tests for health endpoint."""


def test_health(test_client):
    response = test_client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'ok'
