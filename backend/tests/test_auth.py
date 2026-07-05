"""
Tests for authentication endpoints.
"""
import pytest
from datetime import datetime, timedelta
import jwt

from ..models.user import User
from ..db_repository.database import db_session
from ..api.jwt_utils import JWT_ALGORITHM
from .conftest import csrf_headers, login_user, register_user


def test_register(test_client, test_db):
    """Test user registration."""
    response = register_user(test_client)
    assert response.status_code == 201
    assert response.json['code'] == 'USER_CREATED'
    assert response.json['authenticated'] is True


def test_login(test_client, test_db):
    """Test user login sets session cookie."""
    register_user(test_client)
    response = login_user(test_client)
    assert response.status_code == 200
    assert response.json['authenticated'] is True


def test_protected_route(test_client, test_db):
    """Test protected route access via session cookie."""
    register_user(test_client)
    login_user(test_client)
    response = test_client.get('/api/data')
    assert response.status_code == 200


def test_protected_route_bearer_fallback(test_client, test_db, test_app):
    """Bearer header still works for API clients."""
    from ..api.jwt_utils import generate_token

    register_user(test_client, username='beareruser', password='testpass8')
    with test_app.app_context():
        user = User.query.filter_by(username='beareruser').first()
        bearer = generate_token(user.id)
    response = test_client.get(
        '/api/data',
        headers={'Authorization': f'Bearer {bearer}'},
    )
    assert response.status_code == 200


def test_invalid_token_format(test_client, test_db):
    response = test_client.get('/api/data', headers={'Authorization': 'NotBearer token'})
    assert response.status_code == 401


def test_invalid_token(test_client, test_db):
    response = test_client.get('/api/data', headers={'Authorization': 'Bearer invalid-token'})
    assert response.status_code == 401


def test_expired_token(test_client, test_db):
    user = User(username='expuser_expired', password_hash='hashed')
    db_session.add(user)
    db_session.commit()
    expired = jwt.encode(
        {'user_id': user.id, 'exp': datetime.utcnow() - timedelta(hours=1)},
        'test-jwt-secret-key',
        algorithm=JWT_ALGORITHM,
    )
    response = test_client.get(
        '/api/data',
        headers={'Authorization': f'Bearer {expired}'},
    )
    assert response.status_code == 401


def test_duplicate_registration(test_client, test_db):
    payload = {'username': 'dupuser', 'password': 'testpass8'}
    first = test_client.post('/api/register', json=payload, headers=csrf_headers(test_client))
    assert first.status_code == 201
    second = test_client.post('/api/register', json=payload, headers=csrf_headers(test_client))
    assert second.status_code == 400
    assert second.json['code'] == 'USERNAME_EXISTS'


def test_register_rollback_on_error(test_client, test_db, monkeypatch):
    def fail_commit():
        raise RuntimeError('simulated db error')

    monkeypatch.setattr(db_session, 'commit', fail_commit)
    response = test_client.post(
        '/api/register',
        json={'username': 'rollbackuser', 'password': 'testpass8'},
        headers=csrf_headers(test_client),
    )
    assert response.status_code == 500
    assert User.query.filter_by(username='rollbackuser').first() is None

    monkeypatch.undo()
    response = test_client.post(
        '/api/register',
        json={'username': 'rollbackuser2', 'password': 'testpass8'},
        headers=csrf_headers(test_client),
    )
    assert response.status_code == 201


def test_login_wrong_password(test_client, test_db):
    register_user(test_client, username='wrongpass', password='testpass8')
    response = test_client.post(
        '/api/login',
        json={'username': 'wrongpass', 'password': 'wrong'},
        headers=csrf_headers(test_client),
    )
    assert response.status_code == 401


def test_login_oauth_only_user(test_client, test_db):
    user = User(
        username='oauthonly',
        password_hash=None,
        oauth_provider='google',
        oauth_id='123',
    )
    db_session.add(user)
    db_session.commit()
    response = test_client.post(
        '/api/login',
        json={'username': 'oauthonly', 'password': 'anything'},
        headers=csrf_headers(test_client),
    )
    assert response.status_code == 401


def test_login_missing_json(test_client, test_db):
    response = test_client.post('/api/login', headers=csrf_headers(test_client))
    assert response.status_code == 401


def test_session_unauthenticated(test_client, test_db):
    response = test_client.get('/api/auth/session')
    assert response.status_code == 200
    assert response.json['authenticated'] is False


def test_session_authenticated(test_client, test_db):
    register_user(test_client)
    login_user(test_client)
    response = test_client.get('/api/auth/session')
    assert response.status_code == 200
    assert response.json['authenticated'] is True
    assert response.json['username'] == 'testuser'


def test_logout_clears_session(test_client, test_db):
    register_user(test_client)
    login_user(test_client)
    logout = test_client.post('/api/logout', headers=csrf_headers(test_client))
    assert logout.status_code == 200
    session = test_client.get('/api/auth/session')
    assert session.json['authenticated'] is False


def test_csrf_required_on_login(test_client, test_db):
    response = test_client.post('/api/login', json={'username': 'x', 'password': 'y'})
    assert response.status_code == 403
    assert response.json['code'] == 'CSRF_INVALID'


def test_jwt_secret_from_config(test_client, test_db):
    register_user(test_client, username='jwtuser', password='testpass8')
    login_user(test_client, username='jwtuser', password='testpass8')
    assert test_client.get('/api/data').status_code == 200
