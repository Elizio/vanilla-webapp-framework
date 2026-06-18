from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps
from ..models.user import User
from ..db_repository.database import db_session

auth_bp = Blueprint('auth', __name__)

JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = 3600


def _jwt_secret():
    return current_app.config.get('JWT_SECRET_KEY') or current_app.config.get('JWT_SECRET')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, _jwt_secret(), algorithms=[JWT_ALGORITHM])
            current_user = db_session.get(User, data['user_id'])
            if not current_user:
                return jsonify({'message': 'Invalid token'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except (jwt.InvalidTokenError, IndexError):
            return jsonify({'message': 'Invalid token'}), 401
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

    if user and check_password_hash(user.password_hash, data.get('password')):
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION)
        }, _jwt_secret(), algorithm=JWT_ALGORITHM)
        return jsonify({'token': token})

    return jsonify({'message': 'Invalid credentials'}), 401


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
    data = request.get_json()
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'message': 'Username already exists'}), 400

    user = User(
        username=data.get('username'),
        password_hash=generate_password_hash(data.get('password'))
    )
    try:
        db_session.add(user)
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise

    return jsonify({'message': 'User created successfully'}), 201
