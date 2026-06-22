"""Stable API error and success codes for language-neutral responses."""
from flask import jsonify

TOKEN_MISSING = 'TOKEN_MISSING'
TOKEN_EXPIRED = 'TOKEN_EXPIRED'
INVALID_TOKEN = 'INVALID_TOKEN'
INVALID_CREDENTIALS = 'INVALID_CREDENTIALS'
USERNAME_PASSWORD_REQUIRED = 'USERNAME_PASSWORD_REQUIRED'
USERNAME_EXISTS = 'USERNAME_EXISTS'
REGISTRATION_FAILED = 'REGISTRATION_FAILED'
PROVIDER_NOT_CONFIGURED = 'PROVIDER_NOT_CONFIGURED'
NOT_FOUND = 'NOT_FOUND'
INTERNAL_ERROR = 'INTERNAL_ERROR'
USER_CREATED = 'USER_CREATED'


def error_response(code: str, status: int):
    """Build a JSON error response with a stable code.

    Args:
        code: Machine-readable error code (e.g. ``INVALID_CREDENTIALS``).
        status: HTTP status code.

    Returns:
        Tuple of (Flask response, status code).
    """
    return jsonify({'code': code}), status
