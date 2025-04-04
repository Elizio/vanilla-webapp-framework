"""
Tests for authentication endpoints.
"""
import pytest
from ..models.user import User
from ..db_repository.database import db_session

def test_register(test_client, test_db):
    """Test user registration."""
    response = test_client.post('/api/register', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'User created successfully'

def test_login(test_client, test_db):
    """Test user login."""
    # First register a user
    test_client.post('/api/register', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    
    # Then try to login
    response = test_client.post('/api/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 200
    assert 'token' in response.json

def test_protected_route(test_client, test_db):
    """Test protected route access."""
    # First register and login
    test_client.post('/api/register', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    login_response = test_client.post('/api/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    token = login_response.json['token']
    
    # Try to access protected route
    response = test_client.get('/api/data', headers={
        'Authorization': f'Bearer {token}'
    })
    assert response.status_code == 200
    assert response.json['message'] == 'Secure data' 