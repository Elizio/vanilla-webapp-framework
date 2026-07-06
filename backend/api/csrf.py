"""Double-submit CSRF protection for cookie-authenticated SPA requests."""
import secrets
from functools import wraps

from flask import Blueprint, jsonify, make_response, request

from .error_codes import CSRF_INVALID, error_response

csrf_bp = Blueprint('csrf', __name__)

CSRF_COOKIE_NAME = 'csrf_token'
CSRF_HEADER_NAME = 'X-CSRF-Token'


def csrf_protect(f):
    """Require matching CSRF cookie and header on mutating requests."""

    @wraps(f)
    def decorated(*args, **kwargs):
        cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
        header_token = request.headers.get(CSRF_HEADER_NAME)
        if not cookie_token or not header_token or cookie_token != header_token:
            return error_response(CSRF_INVALID, 403)
        return f(*args, **kwargs)

    return decorated


@csrf_bp.route('/api/csrf', methods=['GET'])
def get_csrf():
    """
    Issue a CSRF token for double-submit cookie validation.
    ---
    tags:
      - Authentication
    responses:
      200:
        description: CSRF token for mutating requests
    """
    from flask import current_app

    token = secrets.token_urlsafe(32)
    response = make_response(jsonify({'csrf_token': token}))
    secure = current_app.config.get('APP_PROFILE') == 'production'
    response.set_cookie(
        CSRF_COOKIE_NAME,
        token,
        httponly=False,
        secure=secure,
        samesite='Lax',
        path='/',
    )
    return response
