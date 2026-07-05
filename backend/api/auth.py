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
from .jwt_utils import JWT_ALGORITHM, _jwt_secret
from .session_auth import (
    clear_auth_cookie,
    get_token_from_request,
    set_auth_cookie,
)
from .csrf import csrf_protect
from .rate_limit import rate_limit_auth

auth_bp = Blueprint('auth', __name__)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_request()
        if not token:
            return error_response(TOKEN_MISSING, 401)
        try:
            data = jwt.decode(token, _jwt_secret(), algorithms=[JWT_ALGORITHM])
            current_user = db_session.get(User, data['user_id'])
            if not current_user:
                return error_response(INVALID_TOKEN, 401)
            if not current_user.is_active:
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
        user = db_session.get(User, data['user_id'])
        if not user:
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
      401:
        description: Invalid credentials
      403:
        description: CSRF validation failed
    """
    data = request.get_json(silent=True) or {}
    user = User.query.filter_by(username=data.get('username')).first()

    if user and user.password_hash and check_password_hash(
        user.password_hash, data.get('password')
    ):
        response = jsonify({'authenticated': True, 'username': user.username})
        return set_auth_cookie(response, user.id)

    return error_response(INVALID_CREDENTIALS, 401)


@auth_bp.route('/api/logout', methods=['POST'])
@csrf_protect
def logout():
    """
    Clear the session cookie.
    ---
    tags:
      - Authentication
    responses:
      200:
        description: Logged out
      403:
        description: CSRF validation failed
    """
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
    """
    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password')

    if not username or not password:
        return error_response(USERNAME_PASSWORD_REQUIRED, 400)

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

    response = jsonify({'code': USER_CREATED, 'authenticated': True, 'username': username})
    response.status_code = 201
    return set_auth_cookie(response, user.id)
