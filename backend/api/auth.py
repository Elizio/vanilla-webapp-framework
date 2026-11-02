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
    apply_rotated_refresh,
    clear_session_cookies,
    get_refresh_token_from_request,
    get_token_from_request,
    set_session_cookies,
)
from .refresh_tokens import (
    RotatedRefresh,
    access_session_is_active,
    revoke_all_families,
    revoke_presented_token,
    revoke_session,
    rotate_refresh_token,
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

    Call this on logout-all and on any later password-change or reset
    path (#59). Regular logout of a ``sid`` token revokes one family.
    Logout of a legacy token with no ``sid`` also calls this so that
    token dies immediately (other devices of that user are signed out
    for the remaining access TTL of in-flight pre-deploy JWTs).

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
    A missing ``sid`` is a pre-deploy token and is checked with ``tv``
    only. A present ``sid`` must be a live refresh family for this user.

    Args:
        data: Decoded JWT claims (``user_id``, optional ``tv``, optional
            ``sid``).

    Returns:
        The matching user, or ``None`` when ``user_id`` is missing, the
        row does not exist, ``tv`` does not match, or ``sid`` is forged
        / revoked.
    """
    user = _user_from_tv_payload(data)
    if user is None:
        return None
    if 'sid' in data:
        session_id = data['sid']
        if not isinstance(session_id, str) or not session_id:
            return None
        if not access_session_is_active(session_id, user.id):
            return None
    return user


def _revoke_request_session() -> None:
    """Revoke the session presented on this logout request.

    Prefers JWT ``sid`` (this device only). A legacy access token with
    no ``sid`` bumps ``token_version`` so that JWT dies immediately.
    The refresh cookie, when sent, revokes its family as well.
    """
    token = get_token_from_request()
    if token:
        try:
            data = jwt.decode(token, _jwt_secret(), algorithms=[JWT_ALGORITHM])
        except jwt.InvalidTokenError:
            data = None
        if data is not None:
            user = _user_from_tv_payload(data)
            if user is not None:
                if 'sid' in data:
                    session_id = data['sid']
                    if isinstance(session_id, str) and session_id:
                        revoke_session(session_id, user.id)
                else:
                    bump_token_version(user)
    raw = get_refresh_token_from_request()
    if raw:
        revoke_presented_token(raw)


def _user_from_tv_payload(data: dict) -> User | None:
    """Return the user when ``user_id`` and ``tv`` match, ignoring ``sid``.

    Used by logout so a still-signed JWT can identify the account even
    after its family is already revoked (idempotent logout).

    Args:
        data: Decoded JWT claims.

    Returns:
        The user, or ``None`` when the token cannot be bound to a row.
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
            remember_me:
              type: boolean
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
    remember_me = (request.get_json(silent=True) or {}).get('remember_me') is True
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
        set_session_cookies(response, user, remember_me=remember_me)
        return issue_device_cookie(response, username)

    return error_response(INVALID_CREDENTIALS, 401)


@auth_bp.route('/api/auth/refresh', methods=['POST'])
@csrf_protect
def refresh():
    """
    Rotate the refresh cookie and issue a new access token.
    ---
    tags:
      - Authentication
    responses:
      200:
        description: New access and refresh cookies set
      401:
        description: Refresh token missing, reused, expired, or revoked
      403:
        description: CSRF validation failed or account inactive
    """
    raw = get_refresh_token_from_request()
    if not raw:
        return error_response(INVALID_TOKEN, 401)
    result = rotate_refresh_token(
        raw,
        user_agent=request.headers.get('User-Agent'),
    )
    if result == 'inactive':
        return error_response(ACCOUNT_INACTIVE, 403)
    if not isinstance(result, RotatedRefresh):
        return error_response(INVALID_TOKEN, 401)
    response = jsonify({'authenticated': True, 'username': result.user.username})
    return apply_rotated_refresh(
        response,
        result.user,
        result.raw_token,
        result.cookie_max_age,
        result.family_id,
    )


@auth_bp.route('/api/auth/logout', methods=['POST'])
@csrf_protect
def logout():
    """
    Revoke this browser's session and clear cookies.

    Access tokens that carry this session's ``sid`` fail on the next
    request. Other devices are unchanged. A legacy token with no
    ``sid`` bumps ``token_version`` so it dies immediately.
    ---
    tags:
      - Authentication
    responses:
      200:
        description: Logged out; this session is revoked
      403:
        description: CSRF validation failed
    """
    _revoke_request_session()
    response = jsonify({'authenticated': False})
    return clear_session_cookies(response)


@auth_bp.route('/api/logout', methods=['POST'])
@csrf_protect
def logout_legacy():
    """
    Deprecated alias for logout. Prefer ``POST /api/auth/logout``.

    The access cookie is sent here (``Path`` is ``APP_BASE_PATH``), so
    a ``sid`` token still revokes that family. The refresh cookie is
    not sent at this path. A legacy no-``sid`` access cookie bumps
    ``token_version``.
    ---
    tags:
      - Authentication
    responses:
      200:
        description: Cookies cleared; this session revoked when presented
      403:
        description: CSRF validation failed
    """
    _revoke_request_session()
    response = jsonify({'authenticated': False})
    return clear_session_cookies(response)


@auth_bp.route('/api/auth/logout-all', methods=['POST'])
@csrf_protect
@token_required
def logout_all(current_user):
    """
    Revoke every refresh family and bump ``token_version``.
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: All sessions revoked
      401:
        description: Missing or invalid access token
      403:
        description: CSRF validation failed or account inactive
    """
    bump_token_version(current_user)
    revoke_all_families(current_user.id)
    response = jsonify({'authenticated': False})
    return clear_session_cookies(response)


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
    set_session_cookies(response, user, remember_me=False)
    return issue_device_cookie(response, username)
