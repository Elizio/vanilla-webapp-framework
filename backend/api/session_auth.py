"""HttpOnly cookie helpers for JWT session authentication."""
from flask import current_app, request

from .jwt_utils import JWT_EXPIRATION, generate_token

AUTH_COOKIE_NAME = 'auth_token'


def set_auth_cookie(response, user_id: int):
    """Attach a signed JWT as an httpOnly session cookie.

    Args:
        response: Flask response to mutate.
        user_id: Authenticated user primary key.

    Returns:
        The same response with ``Set-Cookie`` applied.
    """
    token = generate_token(user_id)
    secure = current_app.config.get('APP_PROFILE') == 'production'
    response.set_cookie(
        AUTH_COOKIE_NAME,
        token,
        httponly=True,
        secure=secure,
        samesite='Lax',
        path='/',
        max_age=JWT_EXPIRATION,
    )
    return response


def clear_auth_cookie(response):
    """Remove the session cookie from the client."""
    response.set_cookie(
        AUTH_COOKIE_NAME,
        '',
        expires=0,
        httponly=True,
        secure=current_app.config.get('APP_PROFILE') == 'production',
        samesite='Lax',
        path='/',
    )
    return response


def get_token_from_request() -> str | None:
    """Read JWT from the session cookie or ``Authorization: Bearer`` header."""
    token = request.cookies.get(AUTH_COOKIE_NAME)
    if token:
        return token

    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None

    parts = auth_header.split(' ', 1)
    if len(parts) == 2 and parts[0] == 'Bearer':
        return parts[1]
    return None
