"""Shared JWT helpers for password and OAuth login."""
import jwt
from datetime import datetime, timedelta, timezone
from flask import current_app

JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = 3600


def _jwt_secret():
    return current_app.config.get('JWT_SECRET_KEY') or current_app.config.get('JWT_SECRET')


def generate_token(user_id):
    """Return a signed JWT for the given user id."""
    return jwt.encode({
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(seconds=JWT_EXPIRATION),
    }, _jwt_secret(), algorithm=JWT_ALGORITHM)
