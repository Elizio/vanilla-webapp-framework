"""
Tests for public routes.
"""


def test_public_data(test_client):
    """Test public data endpoint."""
    response = test_client.get('/api/public')
    assert response.status_code == 200
    assert response.json['info'] == 'Hello world'
