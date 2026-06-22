from flask import Blueprint, request, jsonify, current_app
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
    error_response,
)
from .jwt_utils import JWT_ALGORITHM, _jwt_secret, generate_token

auth_bp = Blueprint('auth', __name__)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return error_response(TOKEN_MISSING, 401)
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, _jwt_secret(), algorithms=[JWT_ALGORITHM])
            current_user = db_session.get(User, data['user_id'])
            if not current_user:
                return error_response(INVALID_TOKEN, 401)
        except jwt.ExpiredSignatureError:
            return error_response(TOKEN_EXPIRED, 401)
        except (jwt.InvalidTokenError, IndexError):
            return error_response(INVALID_TOKEN, 401)
        return f(current_user, *args, **kwargs)
    return decorated


@auth_bp.route('/api/login', methods=['POST'])
def login():
    """
    Authenticate a user and return a JWT token.
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
        schema:
          type: object
          properties:
            token:
              type: string
      401:
        description: Invalid credentials
    """
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()

    if user and user.password_hash and check_password_hash(
        user.password_hash, data.get('password')
    ):
        token = generate_token(user.id)
        return jsonify({'token': token})

    return error_response(INVALID_CREDENTIALS, 401)


@auth_bp.route('/api/register', methods=['POST'])
def register():
    """
    Register a new user.
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
    """
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password')

    if not username or not password:
        return error_response(USERNAME_PASSWORD_REQUIRED, 400)

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

    return jsonify({'code': USER_CREATED}), 201
