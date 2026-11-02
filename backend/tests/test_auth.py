"""
Tests for authentication endpoints.
"""

from datetime import datetime, timedelta
import jwt

from ..models.user import User
from ..db_repository.database import db_session
from ..api.jwt_utils import JWT_ALGORITHM
from .conftest import (
    csrf_headers,
    login_user,
    logout_session,
    refresh_session,
    register_user,
)


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
    response = test_client.get(
        '/api/data', headers={'Authorization': 'NotBearer token'}
    )
    assert response.status_code == 401


def test_invalid_token(test_client, test_db):
    response = test_client.get(
        '/api/data', headers={'Authorization': 'Bearer invalid-token'}
    )
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
    first = test_client.post(
        '/api/register', json=payload, headers=csrf_headers(test_client)
    )
    assert first.status_code == 201
    second = test_client.post(
        '/api/register', json=payload, headers=csrf_headers(test_client)
    )
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
    assert response.status_code == 400
    assert response.json['code'] == 'USERNAME_PASSWORD_REQUIRED'


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
    logout = logout_session(test_client)
    assert logout.status_code == 200
    session = test_client.get('/api/auth/session')
    assert session.json['authenticated'] is False


def test_legacy_logout_alias_clears_access_cookie(test_client, test_db):
    """Deprecated POST /api/logout still returns 200 and clears auth_token."""
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


def _inactive_password_user(username='inactiveuser', password='testpass8'):
    """Insert an inactive user with a usable password hash."""
    from werkzeug.security import generate_password_hash

    user = User(
        username=username,
        password_hash=generate_password_hash(password),
        is_active=False,
    )
    db_session.add(user)
    db_session.commit()
    return user


def test_login_inactive_user_correct_password_returns_403(test_client, test_db):
    """Inactive account with the right password is 403 ACCOUNT_INACTIVE."""
    _inactive_password_user()
    response = test_client.post(
        '/api/login',
        json={'username': 'inactiveuser', 'password': 'testpass8'},
        headers=csrf_headers(test_client),
    )
    assert response.status_code == 403
    assert response.json['code'] == 'ACCOUNT_INACTIVE'
    session = test_client.get('/api/auth/session')
    assert session.json['authenticated'] is False


def test_login_inactive_user_wrong_password_returns_401(test_client, test_db):
    """Wrong password on an inactive account still hides account state."""
    _inactive_password_user()
    response = test_client.post(
        '/api/login',
        json={'username': 'inactiveuser', 'password': 'wrong-password'},
        headers=csrf_headers(test_client),
    )
    assert response.status_code == 401
    assert response.json['code'] == 'INVALID_CREDENTIALS'


def test_session_inactive_user_not_authenticated(test_client, test_db):
    """Session bootstrap reports unauthenticated for disabled accounts."""
    user = _inactive_password_user()
    token = jwt.encode(
        {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)},
        'test-jwt-secret-key',
        algorithm=JWT_ALGORITHM,
    )
    response = test_client.get(
        '/api/auth/session',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == 200
    assert response.json['authenticated'] is False


def test_login_missing_password_returns_400(test_client, test_db):
    response = test_client.post(
        '/api/login',
        json={'username': 'someone'},
        headers=csrf_headers(test_client),
    )
    assert response.status_code == 400
    assert response.json['code'] == 'USERNAME_PASSWORD_REQUIRED'


def test_login_non_string_credentials_return_400(test_client, test_db):
    payloads = [
        {'username': ['list-user'], 'password': 'testpass8'},
        {'username': 'someone', 'password': ['list-pass']},
        {'username': 12345, 'password': 'testpass8'},
        {'username': 'someone', 'password': 67890},
    ]
    for payload in payloads:
        response = test_client.post(
            '/api/login',
            json=payload,
            headers=csrf_headers(test_client),
        )
        assert response.status_code == 400, payload
        assert response.json['code'] == 'USERNAME_PASSWORD_REQUIRED', payload


def test_register_non_string_credentials_return_400(test_client, test_db):
    payloads = [
        {'username': 12345, 'password': 'testpass8'},
        {'username': 'newuser', 'password': 67890},
        {'username': ['newuser'], 'password': 'testpass8'},
        {'username': 'newuser', 'password': ['testpass8']},
    ]
    for payload in payloads:
        response = test_client.post(
            '/api/register',
            json=payload,
            headers=csrf_headers(test_client),
        )
        assert response.status_code == 400, payload
        assert response.json['code'] == 'USERNAME_PASSWORD_REQUIRED', payload


def _jwt_without_user_id():
    return jwt.encode(
        {'exp': datetime.utcnow() + timedelta(hours=1)},
        'test-jwt-secret-key',
        algorithm=JWT_ALGORITHM,
    )


def test_jwt_without_user_id_on_protected_route_returns_401(test_client, test_db):
    response = test_client.get(
        '/api/data',
        headers={'Authorization': f'Bearer {_jwt_without_user_id()}'},
    )
    assert response.status_code == 401
    assert response.json['code'] == 'INVALID_TOKEN'


def test_jwt_without_user_id_on_session_is_unauthenticated(test_client, test_db):
    """Session bootstrap treats a JWT without user_id like any other bad token."""
    response = test_client.get(
        '/api/auth/session',
        headers={'Authorization': f'Bearer {_jwt_without_user_id()}'},
    )
    assert response.status_code != 500
    assert response.status_code == 200
    assert response.json == {'authenticated': False}


def test_jwt_non_int_user_id_returns_401(test_client, test_db):
    token = jwt.encode(
        {
            'user_id': 'not-an-int',
            'exp': datetime.utcnow() + timedelta(hours=1),
        },
        'test-jwt-secret-key',
        algorithm=JWT_ALGORITHM,
    )
    protected = test_client.get(
        '/api/data',
        headers={'Authorization': f'Bearer {token}'},
    )
    session = test_client.get(
        '/api/auth/session',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert protected.status_code == 401
    assert protected.json['code'] == 'INVALID_TOKEN'
    assert session.status_code != 500
    assert session.status_code == 200
    assert session.json == {'authenticated': False}


def test_put_login_returns_method_not_allowed(test_client, test_db):
    response = test_client.put('/api/login', json={'username': 'x'})
    assert response.status_code == 405
    assert response.json['code'] == 'METHOD_NOT_ALLOWED'
    allow = {
        part.strip()
        for part in (response.headers.get('Allow') or '').split(',')
        if part.strip()
    }
    assert 'POST' in allow


def _copy_auth_token(client) -> str:
    """Return the current ``auth_token`` cookie value."""
    cookie = client.get_cookie('auth_token')
    assert cookie is not None
    assert cookie.value
    return cookie.value


def test_logout_all_revokes_copied_cookie_token(test_client, test_db):
    """Copied auth_token cookie is 401 after logout-all."""
    register_user(test_client, username='cookierevoke', password='testpass8')
    login_user(test_client, username='cookierevoke', password='testpass8')
    token = _copy_auth_token(test_client)
    assert test_client.get('/api/data').status_code == 200

    logout = test_client.post('/api/auth/logout-all', headers=csrf_headers(test_client))
    assert logout.status_code == 200

    test_client.set_cookie('auth_token', token)
    revoked = test_client.get('/api/data')
    assert revoked.status_code == 401
    assert revoked.json['code'] == 'INVALID_TOKEN'


def test_logout_all_revokes_copied_bearer_token(test_client, test_db):
    """Copied Authorization Bearer JWT is 401 after logout-all."""
    register_user(test_client, username='bearerrevo', password='testpass8')
    login_user(test_client, username='bearerrevo', password='testpass8')
    token = _copy_auth_token(test_client)
    assert (
        test_client.get(
            '/api/data', headers={'Authorization': f'Bearer {token}'}
        ).status_code
        == 200
    )

    logout = test_client.post('/api/auth/logout-all', headers=csrf_headers(test_client))
    assert logout.status_code == 200

    revoked = test_client.get('/api/data', headers={'Authorization': f'Bearer {token}'})
    assert revoked.status_code == 401
    assert revoked.json['code'] == 'INVALID_TOKEN'


def test_logout_all_revokes_other_sessions(test_client, test_db, test_app):
    """logout-all invalidates every session for that user."""
    register_user(test_client, username='allsessions', password='testpass8')
    login_user(test_client, username='allsessions', password='testpass8')
    first_token = _copy_auth_token(test_client)

    other = test_app.test_client()
    login_user(other, username='allsessions', password='testpass8')
    second_token = _copy_auth_token(other)

    logout = test_client.post('/api/auth/logout-all', headers=csrf_headers(test_client))
    assert logout.status_code == 200

    first = test_client.get(
        '/api/data', headers={'Authorization': f'Bearer {first_token}'}
    )
    second = other.get('/api/data', headers={'Authorization': f'Bearer {second_token}'})
    assert first.status_code == 401
    assert first.json['code'] == 'INVALID_TOKEN'
    assert second.status_code == 401
    assert second.json['code'] == 'INVALID_TOKEN'


def test_logout_revokes_this_device_access_immediately(test_client, test_db, test_app):
    """Copied access JWT is 401 on the next request after this device logs out."""
    register_user(test_client, username='sidlogout', password='testpass8')
    login_user(test_client, username='sidlogout', password='testpass8')
    token = _copy_auth_token(test_client)
    assert test_client.get('/api/data').status_code == 200
    assert (
        test_client.get(
            '/api/data', headers={'Authorization': f'Bearer {token}'}
        ).status_code
        == 200
    )

    assert logout_session(test_client).status_code == 200

    test_client.set_cookie('auth_token', token)
    cookie_revoked = test_client.get('/api/data')
    assert cookie_revoked.status_code == 401
    assert cookie_revoked.json['code'] == 'INVALID_TOKEN'

    bearer = test_app.test_client()
    bearer_revoked = bearer.get(
        '/api/data', headers={'Authorization': f'Bearer {token}'}
    )
    assert bearer_revoked.status_code == 401
    assert bearer_revoked.json['code'] == 'INVALID_TOKEN'


def test_family_logout_keeps_other_device_access(test_client, test_db, test_app):
    """Regular logout kills this device; other devices keep access and refresh."""
    register_user(test_client, username='onefamily', password='testpass8')
    login_user(test_client, username='onefamily', password='testpass8')
    this_token = _copy_auth_token(test_client)

    other = test_app.test_client()
    login_user(other, username='onefamily', password='testpass8')
    other_token = _copy_auth_token(other)
    other_refresh = _copy_refresh_token(other)

    logout = logout_session(test_client)
    assert logout.status_code == 200

    this_revoked = test_app.test_client().get(
        '/api/data', headers={'Authorization': f'Bearer {this_token}'}
    )
    assert this_revoked.status_code == 401
    assert this_revoked.json['code'] == 'INVALID_TOKEN'

    still = other.get('/api/data', headers={'Authorization': f'Bearer {other_token}'})
    assert still.status_code == 200
    rotated = refresh_session(other)
    assert rotated.status_code == 200
    assert _copy_refresh_token(other) != other_refresh


def test_legacy_access_token_without_sid_survives_deploy(
    test_client, test_db, test_app
):
    """Tokens minted before ``sid`` stay valid; missing ``tv`` still counts as 0."""
    register_user(test_client, username='legacysid', password='testpass8')
    user = User.query.filter_by(username='legacysid').first()
    assert user is not None
    token = jwt.encode(
        {
            'user_id': user.id,
            'tv': 0,
            'exp': datetime.utcnow() + timedelta(hours=1),
        },
        'test-jwt-secret-key',
        algorithm=JWT_ALGORITHM,
    )
    anon = test_app.test_client()
    response = anon.get('/api/data', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200


def test_legacy_access_token_without_sid_dies_on_logout(test_client, test_db, test_app):
    """Logging out with a no-``sid`` JWT bumps ``tv`` so that token is 401."""
    register_user(test_client, username='legacylogout', password='testpass8')
    user = User.query.filter_by(username='legacylogout').first()
    assert user is not None
    token = jwt.encode(
        {
            'user_id': user.id,
            'tv': 0,
            'exp': datetime.utcnow() + timedelta(hours=1),
        },
        'test-jwt-secret-key',
        algorithm=JWT_ALGORITHM,
    )
    anon = test_app.test_client()
    headers = {
        **csrf_headers(anon),
        'Authorization': f'Bearer {token}',
    }
    logout = anon.post('/api/auth/logout', headers=headers)
    assert logout.status_code == 200
    revoked = anon.get('/api/data', headers={'Authorization': f'Bearer {token}'})
    assert revoked.status_code == 401
    assert revoked.json['code'] == 'INVALID_TOKEN'
    bumped = User.query.filter_by(username='legacylogout').one()
    assert int(bumped.token_version or 0) == 1


def test_unknown_sid_claim_returns_401(test_client, test_db, test_app):
    """A signed JWT whose ``sid`` is not a live family is rejected."""
    register_user(test_client, username='badsid', password='testpass8')
    user = User.query.filter_by(username='badsid').first()
    assert user is not None
    token = jwt.encode(
        {
            'user_id': user.id,
            'tv': 0,
            'sid': '00000000-0000-4000-8000-000000000000',
            'exp': datetime.utcnow() + timedelta(hours=1),
        },
        'test-jwt-secret-key',
        algorithm=JWT_ALGORITHM,
    )
    anon = test_app.test_client()
    response = anon.get('/api/data', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 401
    assert response.json['code'] == 'INVALID_TOKEN'


def test_non_string_sid_claim_returns_401(test_client, test_db, test_app):
    """A ``sid`` claim that is not a string is rejected."""
    register_user(test_client, username='intsid', password='testpass8')
    user = User.query.filter_by(username='intsid').first()
    assert user is not None
    token = jwt.encode(
        {
            'user_id': user.id,
            'tv': 0,
            'sid': 1,
            'exp': datetime.utcnow() + timedelta(hours=1),
        },
        'test-jwt-secret-key',
        algorithm=JWT_ALGORITHM,
    )
    anon = test_app.test_client()
    response = anon.get('/api/data', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 401
    assert response.json['code'] == 'INVALID_TOKEN'


def test_empty_sid_claim_returns_401(test_client, test_db, test_app):
    """A present but empty ``sid`` is rejected, not treated as legacy."""
    register_user(test_client, username='emptysid', password='testpass8')
    user = User.query.filter_by(username='emptysid').first()
    assert user is not None
    token = jwt.encode(
        {
            'user_id': user.id,
            'tv': 0,
            'sid': '',
            'exp': datetime.utcnow() + timedelta(hours=1),
        },
        'test-jwt-secret-key',
        algorithm=JWT_ALGORITHM,
    )
    anon = test_app.test_client()
    response = anon.get('/api/data', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 401
    assert response.json['code'] == 'INVALID_TOKEN'


def test_foreign_sid_claim_returns_401(test_client, test_db, test_app):
    """Alice's JWT carrying Bob's live family id is 401; Bob stays signed in."""
    register_user(test_client, username='sidalice', password='testpass8')
    login_user(test_client, username='sidalice', password='testpass8')
    alice = User.query.filter_by(username='sidalice').one()

    bob_client = test_app.test_client()
    register_user(bob_client, username='sidbob', password='testpass8')
    login_user(bob_client, username='sidbob', password='testpass8')
    bob_token = _copy_auth_token(bob_client)
    bob_sid = jwt.decode(
        bob_token,
        'test-jwt-secret-key',
        algorithms=[JWT_ALGORITHM],
    )['sid']
    assert isinstance(bob_sid, str) and bob_sid

    forged = jwt.encode(
        {
            'user_id': alice.id,
            'tv': int(alice.token_version or 0),
            'sid': bob_sid,
            'exp': datetime.utcnow() + timedelta(hours=1),
        },
        'test-jwt-secret-key',
        algorithm=JWT_ALGORITHM,
    )
    stolen = test_app.test_client().get(
        '/api/data', headers={'Authorization': f'Bearer {forged}'}
    )
    assert stolen.status_code == 401
    assert stolen.json['code'] == 'INVALID_TOKEN'
    assert bob_client.get('/api/data').status_code == 200


def test_bump_token_version_revokes_sid_tokens(test_client, test_db, test_app):
    """Password-reset style ``bump_token_version`` kills every access JWT."""
    from ..api.auth import bump_token_version

    register_user(test_client, username='pwdreset', password='testpass8')
    login_user(test_client, username='pwdreset', password='testpass8')
    token = _copy_auth_token(test_client)
    user = User.query.filter_by(username='pwdreset').first()
    assert user is not None
    user = db_session.get(User, user.id)
    assert user is not None
    bump_token_version(user)
    db_session.expire_all()

    revoked = test_app.test_client().get(
        '/api/data', headers={'Authorization': f'Bearer {token}'}
    )
    assert revoked.status_code == 401
    assert revoked.json['code'] == 'INVALID_TOKEN'


def test_jwt_without_tv_accepted_as_version_zero(test_client, test_db, test_app):
    """In-flight tokens minted before the ``tv`` claim stay valid at version 0."""
    register_user(test_client, username='legacytv', password='testpass8')
    user = User.query.filter_by(username='legacytv').first()
    assert user is not None
    assert int(user.token_version or 0) == 0
    token = jwt.encode(
        {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)},
        'test-jwt-secret-key',
        algorithm=JWT_ALGORITHM,
    )
    anon = test_app.test_client()
    response = anon.get('/api/data', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200


def test_stale_logout_does_not_revoke_new_session(test_client, test_db, test_app):
    """Replaying logout-all with an already-revoked JWT must not bump a new session."""
    register_user(test_client, username='stalelogout', password='testpass8')
    login_user(test_client, username='stalelogout', password='testpass8')
    old_token = _copy_auth_token(test_client)
    test_client.post('/api/auth/logout-all', headers=csrf_headers(test_client))

    login_user(test_client, username='stalelogout', password='testpass8')
    assert test_client.get('/api/data').status_code == 200

    stale = test_app.test_client()
    replay = stale.post(
        '/api/auth/logout-all',
        headers={
            **csrf_headers(stale),
            'Authorization': f'Bearer {old_token}',
        },
    )
    assert replay.status_code == 401
    assert test_client.get('/api/data').status_code == 200


def test_logout_preserves_auth_device_cookie(test_client, test_db):
    """Logout must not drop the trusted ``auth_device`` cookie."""
    from ..api.rate_limit import DEVICE_COOKIE_NAME

    register_user(test_client, username='keepdevice', password='testpass8')
    login_user(test_client, username='keepdevice', password='testpass8')
    device = test_client.get_cookie(DEVICE_COOKIE_NAME)
    assert device is not None
    assert device.value

    logout = logout_session(test_client)
    assert logout.status_code == 200
    after = test_client.get_cookie(DEVICE_COOKIE_NAME)
    assert after is not None
    assert after.value == device.value


def test_login_after_logout_issues_working_token(test_client, test_db):
    """A new login after logout must mint a JWT that matches the new version."""
    register_user(test_client, username='relogin', password='testpass8')
    login_user(test_client, username='relogin', password='testpass8')
    logout_session(test_client)
    login_user(test_client, username='relogin', password='testpass8')
    assert test_client.get('/api/data').status_code == 200
    session = test_client.get('/api/auth/session')
    assert session.json['authenticated'] is True


def test_revoked_token_session_is_unauthenticated(test_client, test_db):
    """GET /api/auth/session treats a stale ``tv`` like any other bad token."""
    register_user(test_client, username='sessiontv', password='testpass8')
    login_user(test_client, username='sessiontv', password='testpass8')
    token = _copy_auth_token(test_client)
    test_client.post('/api/auth/logout-all', headers=csrf_headers(test_client))
    session = test_client.get(
        '/api/auth/session',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert session.status_code == 200
    assert session.json == {'authenticated': False}


def test_non_int_tv_claim_returns_401(test_client, test_db, test_app):
    """A ``tv`` claim that is not an int is rejected, not coerced."""
    register_user(test_client, username='badtv', password='testpass8')
    user = User.query.filter_by(username='badtv').first()
    assert user is not None
    token = jwt.encode(
        {
            'user_id': user.id,
            'tv': '0',
            'exp': datetime.utcnow() + timedelta(hours=1),
        },
        'test-jwt-secret-key',
        algorithm=JWT_ALGORITHM,
    )
    anon = test_app.test_client()
    response = anon.get('/api/data', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 401
    assert response.json['code'] == 'INVALID_TOKEN'


def _copy_refresh_token(client) -> str:
    """Return the current ``refresh_token`` cookie value."""
    cookie = client.get_cookie('refresh_token', path='/api/auth')
    assert cookie is not None
    assert cookie.value
    return cookie.value


def test_login_sets_refresh_cookie(test_client, test_db):
    """Login and register issue a refresh cookie under Path=/api/auth."""
    register = register_user(test_client, username='refreshuser', password='testpass8')
    assert register.status_code == 201
    assert _copy_refresh_token(test_client)
    login_user(test_client, username='refreshuser', password='testpass8')
    assert _copy_refresh_token(test_client)


def test_access_token_includes_iat(test_client, test_db):
    """New access JWTs carry iat plus tv."""
    register_user(test_client, username='iatuser', password='testpass8')
    login_user(test_client, username='iatuser', password='testpass8')
    payload = jwt.decode(
        _copy_auth_token(test_client),
        'test-jwt-secret-key',
        algorithms=[JWT_ALGORITHM],
    )
    assert 'iat' in payload
    assert payload['tv'] == 0
    assert payload['user_id']
    assert isinstance(payload.get('sid'), str) and payload['sid']


def test_refresh_rotates_token(test_client, test_db):
    """A successful refresh marks the old token used and issues a new pair."""
    from ..models.refresh_token import RefreshToken
    from ..api.refresh_tokens import hash_refresh_token

    register_user(test_client, username='rotator', password='testpass8')
    login_user(test_client, username='rotator', password='testpass8')
    old_refresh = _copy_refresh_token(test_client)

    response = refresh_session(test_client)
    assert response.status_code == 200
    assert response.json['authenticated'] is True
    new_refresh = _copy_refresh_token(test_client)
    assert new_refresh != old_refresh
    assert test_client.get('/api/data').status_code == 200

    used = RefreshToken.query.filter_by(
        token_hash=hash_refresh_token(old_refresh)
    ).one()
    assert used.used_at is not None
    assert used.revoked_at is None
    new_sid = jwt.decode(
        _copy_auth_token(test_client),
        'test-jwt-secret-key',
        algorithms=[JWT_ALGORITHM],
    )['sid']
    assert new_sid == used.family_id


def test_refresh_reuse_within_grace_issues_sibling(test_client, test_db):
    """Presenting the just-rotated token inside 30 s issues a sibling."""
    register_user(test_client, username='graceuser', password='testpass8')
    login_user(test_client, username='graceuser', password='testpass8')
    first = _copy_refresh_token(test_client)

    assert refresh_session(test_client).status_code == 200
    second = _copy_refresh_token(test_client)

    test_client.set_cookie('refresh_token', first, path='/api/auth')
    sibling = refresh_session(test_client)
    assert sibling.status_code == 200
    third = _copy_refresh_token(test_client)
    assert third not in {first, second}

    test_client.set_cookie('refresh_token', second, path='/api/auth')
    assert refresh_session(test_client).status_code == 200


def test_refresh_reuse_after_grace_revokes_family(test_client, test_db, monkeypatch):
    """Presenting a used token after the grace window revokes the family."""
    from datetime import timedelta

    from ..api import refresh_tokens as rt

    class Clock:
        def __init__(self):
            self.now = rt.utc_now()

        def __call__(self):
            return self.now

        def advance(self, seconds):
            self.now = self.now + timedelta(seconds=seconds)

    clock = Clock()
    monkeypatch.setattr(rt, 'utc_now', clock)

    register_user(test_client, username='reuseuser', password='testpass8')
    login_user(test_client, username='reuseuser', password='testpass8')
    first = _copy_refresh_token(test_client)
    assert refresh_session(test_client).status_code == 200
    current = _copy_refresh_token(test_client)

    clock.advance(31)
    test_client.set_cookie('refresh_token', first, path='/api/auth')
    reused = refresh_session(test_client)
    assert reused.status_code == 401
    assert reused.json['code'] == 'INVALID_TOKEN'

    test_client.set_cookie('refresh_token', current, path='/api/auth')
    assert refresh_session(test_client).status_code == 401


def test_refresh_reuse_after_grace_revokes_access(
    test_client, test_db, test_app, monkeypatch
):
    """Reuse detection revokes the family so in-flight access JWTs are 401."""
    from ..api import refresh_tokens as rt

    class Clock:
        def __init__(self):
            self.now = rt.utc_now()

        def __call__(self):
            return self.now

        def advance(self, seconds):
            self.now = self.now + timedelta(seconds=seconds)

    clock = Clock()
    monkeypatch.setattr(rt, 'utc_now', clock)

    register_user(test_client, username='reuseaccess', password='testpass8')
    login_user(test_client, username='reuseaccess', password='testpass8')
    first = _copy_refresh_token(test_client)
    access = _copy_auth_token(test_client)
    assert refresh_session(test_client).status_code == 200

    clock.advance(31)
    test_client.set_cookie('refresh_token', first, path='/api/auth')
    reused = refresh_session(test_client)
    assert reused.status_code == 401
    assert reused.json['code'] == 'INVALID_TOKEN'

    revoked = test_app.test_client().get(
        '/api/data', headers={'Authorization': f'Bearer {access}'}
    )
    assert revoked.status_code == 401
    assert revoked.json['code'] == 'INVALID_TOKEN'


def test_expired_family_sid_returns_401(test_client, test_db, test_app):
    """An expired family cannot refresh; leftover access is 401 after purge."""
    from ..models.refresh_token import RefreshToken

    register_user(test_client, username='expfam', password='testpass8')
    login_user(test_client, username='expfam', password='testpass8')
    access = _copy_auth_token(test_client)
    refresh = _copy_refresh_token(test_client)

    past = datetime.utcnow() - timedelta(seconds=1)
    RefreshToken.query.update(
        {
            RefreshToken.family_expires_at: past,
            RefreshToken.expires_at: past,
        },
        synchronize_session=False,
    )
    db_session.commit()

    test_client.set_cookie('refresh_token', refresh, path='/api/auth')
    expired_refresh = refresh_session(test_client)
    assert expired_refresh.status_code == 401
    assert expired_refresh.json['code'] == 'INVALID_TOKEN'

    login_user(test_client, username='expfam', password='testpass8')
    leftover = test_app.test_client().get(
        '/api/data', headers={'Authorization': f'Bearer {access}'}
    )
    assert leftover.status_code == 401
    assert leftover.json['code'] == 'INVALID_TOKEN'
    assert test_client.get('/api/data').status_code == 200


def test_logout_revokes_refresh_family(test_client, test_db):
    """Logout revokes the family; a later refresh with the old cookie is 401."""
    register_user(test_client, username='logoutfam', password='testpass8')
    login_user(test_client, username='logoutfam', password='testpass8')
    refresh = _copy_refresh_token(test_client)
    assert logout_session(test_client).status_code == 200

    test_client.set_cookie('refresh_token', refresh, path='/api/auth')
    response = refresh_session(test_client)
    assert response.status_code == 401
    assert response.json['code'] == 'INVALID_TOKEN'


def test_logout_all_rejects_refresh(test_client, test_db):
    """logout-all bumps tv so every refresh family fails."""
    register_user(test_client, username='logoutallr', password='testpass8')
    login_user(test_client, username='logoutallr', password='testpass8')
    refresh = _copy_refresh_token(test_client)
    access = _copy_auth_token(test_client)
    assert (
        test_client.post(
            '/api/auth/logout-all', headers=csrf_headers(test_client)
        ).status_code
        == 200
    )

    test_client.set_cookie('refresh_token', refresh, path='/api/auth')
    assert refresh_session(test_client).status_code == 401
    revoked = test_client.get(
        '/api/data', headers={'Authorization': f'Bearer {access}'}
    )
    assert revoked.status_code == 401


def test_refresh_expired_token_returns_401(test_client, test_db, monkeypatch):
    """A session refresh token past its server TTL cannot rotate."""
    from datetime import timedelta

    from ..api import refresh_tokens as rt

    class Clock:
        def __init__(self):
            self.now = rt.utc_now()

        def __call__(self):
            return self.now

        def advance(self, seconds):
            self.now = self.now + timedelta(seconds=seconds)

    clock = Clock()
    monkeypatch.setattr(rt, 'utc_now', clock)

    register_user(test_client, username='expiredref', password='testpass8')
    login_user(test_client, username='expiredref', password='testpass8')
    clock.advance(24 * 3600 + 1)
    response = refresh_session(test_client)
    assert response.status_code == 401
    assert response.json['code'] == 'INVALID_TOKEN'


def test_inactive_user_cannot_refresh(test_client, test_db):
    """An inactive account cannot rotate a still-valid refresh token."""
    register_user(test_client, username='deadref', password='testpass8')
    login_user(test_client, username='deadref', password='testpass8')
    User.query.filter_by(username='deadref').update({'is_active': False})
    User.query.session.commit()
    response = refresh_session(test_client)
    assert response.status_code == 403
    assert response.json['code'] == 'ACCOUNT_INACTIVE'


def test_bearer_access_works_refresh_header_ignored(test_client, test_db, test_app):
    """Bearer access JWTs work; a refresh token in Authorization is ignored."""
    from ..api.jwt_utils import generate_token

    register_user(test_client, username='bearerok', password='testpass8')
    user = User.query.filter_by(username='bearerok').first()
    with test_app.app_context():
        access = generate_token(user.id, user.token_version)
    assert (
        test_client.get(
            '/api/data', headers={'Authorization': f'Bearer {access}'}
        ).status_code
        == 200
    )

    refresh = _copy_refresh_token(test_client)
    anon = test_app.test_client()
    protected = anon.get('/api/data', headers={'Authorization': f'Bearer {refresh}'})
    assert protected.status_code == 401

    ignored = anon.post(
        '/api/auth/refresh',
        headers={
            **csrf_headers(anon),
            'Authorization': f'Bearer {refresh}',
        },
    )
    assert ignored.status_code == 401
    assert ignored.json['code'] == 'INVALID_TOKEN'


def test_refresh_requires_csrf(test_client, test_db):
    register_user(test_client, username='csrfref', password='testpass8')
    login_user(test_client, username='csrfref', password='testpass8')
    response = test_client.post('/api/auth/refresh')
    assert response.status_code == 403
    assert response.json['code'] == 'CSRF_INVALID'
