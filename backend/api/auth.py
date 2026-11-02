"""Password login, registration, session status, and JWT gate."""

from flask import Blueprint, jsonify, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps
from ..models.user import User
from ..db_repository.database import db_session
from .error_codes import (
    TOKEN_MISSING,
    TOKEN_EXPIRED,
    INVALID_TOKEN,
    INVALID_CREDENTIALS,
    USERNAME_PASSWORD_REQUIRED,
    USERNAME_EXISTS,
    REGISTRATION_FAILED,
    USER_CREATED,
    PASSWORD_TOO_SHORT,
    ACCOUNT_INACTIVE,
    error_response,
)
from .jwt_utils import (
    JWT_ALGORITHM,
    _jwt_secret,
    token_version_matches,
)
from .session_auth import (
    clear_auth_cookie,
    get_token_from_request,
    set_auth_cookie,
)
from .csrf import csrf_protect
from .rate_limit import (
    issue_device_cookie,
    rate_limit_auth,
    reset_failed_logins,
    username_login_blocked,
)

auth_bp = Blueprint('auth', __name__)

_DUMMY_PASSWORD_HASH: str | None = None


def _dummy_password_hash() -> str:
    """Return a cached dummy hash so unknown usernames still pay scrypt."""
    global _DUMMY_PASSWORD_HASH
    if _DUMMY_PASSWORD_HASH is None:
        _DUMMY_PASSWORD_HASH = generate_password_hash('not-a-real-password')
    return _DUMMY_PASSWORD_HASH


def user_may_authenticate(user: User) -> bool:
    """Return True if the account is allowed to start or keep a session.

    Args:
        user: Loaded user row.

    Returns:
        ``False`` when the account has been deactivated.
    """
    return bool(user.is_active)


def _user_id_from_payload(data: dict) -> int | None:
    """Return ``user_id`` from a JWT payload when it is a real int."""
    user_id = data.get('user_id')
    if isinstance(user_id, int) and not isinstance(user_id, bool):
        return user_id
    return None


def _read_username_password():
    """Parse username and password from JSON, requiring both to be strings.

    Returns:
        ``((username, password), None)`` on success, or
        ``(None, error_response(...))`` when validation fails.
    """
    data = request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')
    if not isinstance(username, str) or not isinstance(password, str):
        return None, error_response(USERNAME_PASSWORD_REQUIRED, 400)
    username = username.strip()
    if not username or not password:
        return None, error_response(USERNAME_PASSWORD_REQUIRED, 400)
    return (username, password), None


def bump_token_version(user: User) -> int:
    """Increment ``users.token_version`` so existing JWTs fail ``tv`` checks.

    Call this on logout and on any later password-change or reset path
    (#59) or logout-all (#60). There is no password-change route today.

    Args:
        user: Persisted user row whose tokens should be revoked.

    Returns:
        The new token version.
    """
    user.token_version = int(user.token_version or 0) + 1
    db_session.commit()
    return user.token_version


def _authenticate_token_payload(data: dict) -> User | None:
    """Return the user for a decoded JWT, or ``None`` if it is invalid.

    Does not check ``is_active``; callers apply ``user_may_authenticate``.

    Args:
        data: Decoded JWT claims (``user_id``, optional ``tv``).

    Returns:
        The matching user, or ``None`` when ``user_id`` is missing, the
        row does not exist, or ``tv`` does not match ``users.token_version``.
    """
    user_id = _user_id_from_payload(data)
    if user_id is None:
        return None
    user = db_session.get(User, user_id)
    if not user:
        return None
    if not token_version_matches(data, int(user.token_version or 0)):
        return None
    return user


def token_required(f):
    """Require a valid JWT and an active user; inject ``current_user``."""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return error_response(TOKEN_MISSING, 401)
        try:
            data = jwt.decode(token, _jwt_secret(), algorithms=[JWT_ALGORITHM])
            current_user = _authenticate_token_payload(data)
            if current_user is None:
                return error_response(INVALID_TOKEN, 401)
            if not user_may_authenticate(current_user):
                return error_response(ACCOUNT_INACTIVE, 403)
        except jwt.ExpiredSignatureError:
            return error_response(TOKEN_EXPIRED, 401)
        except jwt.InvalidTokenError:
            return error_response(INVALID_TOKEN, 401)
        return f(current_user, *args, **kwargs)

    return decorated


@auth_bp.route('/api/auth/session', methods=['GET'])
def session_status():
    """
    Return whether the browser session is authenticated.
    ---
    tags:
      - Authentication
    responses:
      200:
        description: Session state
    """
    token = get_token_from_request()
    if not token:
        return jsonify({'authenticated': False})

    try:
        data = jwt.decode(token, _jwt_secret(), algorithms=[JWT_ALGORITHM])
        user = _authenticate_token_payload(data)
        if not user or not user_may_authenticate(user):
            return jsonify({'authenticated': False})
        return jsonify({'authenticated': True, 'username': user.username})
    except jwt.InvalidTokenError:
        return jsonify({'authenticated': False})


@auth_bp.route('/api/login', methods=['POST'])
@rate_limit_auth
@csrf_protect
def login():
    """
    Authenticate a user and set a session cookie.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
          required:
            - username
            - password
    responses:
      200:
        description: Login successful
      400:
        description: Missing or non-string username/password
      401:
        description: Invalid credentials
      403:
        description: CSRF validation failed or account inactive
      429:
        description: Rate limit exceeded
    """
    credentials, error = _read_username_password()
    if error:
        return error
    username, password = credentials
    blocked = username_login_blocked(username)
    if blocked is not None:
        return blocked
    user = User.query.filter_by(username=username).first()
    stored_hash = (
        user.password_hash if user and user.password_hash else _dummy_password_hash()
    )
    password_ok = check_password_hash(stored_hash, password)
    if user and user.password_hash and password_ok:
        if not user_may_authenticate(user):
            return error_response(ACCOUNT_INACTIVE, 403)
        reset_failed_logins(username)
        response = jsonify({'authenticated': True, 'username': user.username})
        set_auth_cookie(response, user.id, user.token_version)
        return issue_device_cookie(response, username)

    return error_response(INVALID_CREDENTIALS, 401)


@auth_bp.route('/api/logout', methods=['POST'])
@csrf_protect
def logout():
    """
    Revoke this user's JWTs and clear the session cookie.

    Increments ``users.token_version`` so every access token for the
    account fails ``tv`` checks (cookie or ``Authorization: Bearer``).
    A stale or missing token is ignored; the cookie is still cleared.
    ---
    tags:
      - Authentication
    responses:
      200:
        description: Logged out; existing JWTs for this user are revoked
      403:
        description: CSRF validation failed
    """
    token = get_token_from_request()
    if token:
        try:
            data = jwt.decode(token, _jwt_secret(), algorithms=[JWT_ALGORITHM])
            user = _authenticate_token_payload(data)
            if user is not None:
                bump_token_version(user)
        except jwt.InvalidTokenError:
            pass
    response = jsonify({'authenticated': False})
    return clear_auth_cookie(response)


@auth_bp.route('/api/register', methods=['POST'])
@rate_limit_auth
@csrf_protect
def register():
    """
    Register a new user and start a session.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
          required:
            - username
            - password
    responses:
      201:
        description: User created successfully
      400:
        description: Username already exists
      403:
        description: CSRF validation failed
      429:
        description: Rate limit exceeded
    """
    credentials, error = _read_username_password()
    if error:
        return error
    username, password = credentials

    if len(password) < 8:
        return error_response(PASSWORD_TOO_SHORT, 400)

    if User.query.filter_by(username=username).first():
        return error_response(USERNAME_EXISTS, 400)

    user = User(
        username=username,
        password_hash=generate_password_hash(password),
    )
    try:
        db_session.add(user)
        db_session.commit()
    except Exception as exc:
        db_session.rollback()
        current_app.logger.error('Registration failed: %s', exc)
        return error_response(REGISTRATION_FAILED, 500)

    response = jsonify(
        {'code': USER_CREATED, 'authenticated': True, 'username': username}
    )
    response.status_code = 201
    set_auth_cookie(response, user.id, user.token_version)
    return issue_device_cookie(response, username)
