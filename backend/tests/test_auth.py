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

def test_protected_route_missing_token(test_client, test_db):
    response = test_client.get('/api/data')
    assert response.status_code == 401
    assert response.json['message'] == 'Token is missing'


def test_protected_route_malformed_token(test_client, test_db):
    response = test_client.get('/api/data', headers={'Authorization': 'NotBearer token'})
    assert response.status_code == 401


def test_protected_route_invalid_token(test_client, test_db):
    response = test_client.get('/api/data', headers={'Authorization': 'Bearer invalid-token'})
    assert response.status_code == 401


def test_protected_route_expired_token(test_client, test_db):
    import jwt
    from datetime import datetime, timedelta

    test_client.post('/api/register', json={'username': 'expuser_expired', 'password': 'testpass'})
    expired = jwt.encode(
        {'user_id': 1, 'exp': datetime.utcnow() - timedelta(hours=1)},
        'test-jwt-secret-key',
        algorithm='HS256',
    )
    response = test_client.get('/api/data', headers={'Authorization': f'Bearer {expired}'})
    assert response.status_code == 401
    assert response.json['message'] == 'Token has expired'


def test_register_duplicate_user(test_client, test_db):
    payload = {'username': 'dupuser', 'password': 'testpass'}
    test_client.post('/api/register', json=payload)
    response = test_client.post('/api/register', json=payload)
    assert response.status_code == 400
    assert response.json['message'] == 'Username already exists'


def test_register_rollback_on_commit_failure(test_app, test_db, monkeypatch):
    from backend.db_repository.database import db_session

    real_commit = db_session.commit
    attempts = {'count': 0}

    def maybe_fail_commit():
        attempts['count'] += 1
        if attempts['count'] == 1:
            raise RuntimeError('commit failed')
        return real_commit()

    monkeypatch.setattr(db_session, 'commit', maybe_fail_commit)

    test_app.config['PROPAGATE_EXCEPTIONS'] = False
    client = test_app.test_client()

    response = client.post('/api/register', json={'username': 'rollbackuser', 'password': 'testpass'})
    assert response.status_code == 500

    response = client.post('/api/register', json={'username': 'rollbackuser2', 'password': 'testpass'})
    assert response.status_code == 201


def test_login_oauth_only_user_returns_401(test_client, test_db):
    user = User(
        username='oauthonly',
        oauth_provider='google',
        oauth_id='999',
        password_hash=None,
    )
    db_session.add(user)
    db_session.commit()

    response = test_client.post('/api/login', json={
        'username': 'oauthonly',
        'password': 'anything',
    })
    assert response.status_code == 401


def test_jwt_uses_app_config_secret(test_client, test_db):
    import jwt

    test_client.post('/api/register', json={'username': 'jwtuser', 'password': 'testpass'})
    login = test_client.post('/api/login', json={'username': 'jwtuser', 'password': 'testpass'})
    token = login.json['token']

    decoded = jwt.decode(token, 'test-jwt-secret-key', algorithms=['HS256'])
    assert decoded['user_id'] == 1
