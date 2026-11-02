"""Double-submit CSRF protection for cookie-authenticated SPA requests."""

import hmac
import secrets
from functools import wraps

from flask import Blueprint, jsonify, make_response, request

from ..config.cookie_names import LEGACY_CSRF_COOKIE_NAME
from .cookie_path import (
    app_cookie_path,
    cookie_secure,
    csrf_cookie_name,
    expire_legacy_root_cookie,
    expire_replaced_cookie,
)
from .error_codes import CSRF_INVALID, error_response

csrf_bp = Blueprint('csrf', __name__)

CSRF_HEADER_NAME = 'X-CSRF-Token'


def _csrf_cookie_values() -> list[str]:
    """Return CSRF cookie values under the live name and the legacy name.

    Safari on iPhone can send duplicate ``Cookie`` keys (a foreign or
    leftover Path=/ value first). ``request.cookies.get()`` keeps only the
    first, so callers must consider every value.

    Legacy ``csrf_token`` stays readable until ``REFRESH_TOKEN_TTL_DAYS``
    plus 7 days after the namespaced-cookie deploy; keep expiring it.
    """
    names = (csrf_cookie_name(), LEGACY_CSRF_COOKIE_NAME)
    values: list[str] = []
    for name in names:
        values.extend(token for token in request.cookies.getlist(name) if token)
    raw = request.headers.get('Cookie') or ''
    if raw:
        wanted = set(names)
        for part in raw.split(';'):
            part = part.strip()
            if not part or '=' not in part:
                continue
            key, _, value = part.partition('=')
            if key.strip() in wanted and value:
                values.append(value)
    unique: list[str] = []
    seen: set[str] = set()
    for token in values:
        if token not in seen:
            seen.add(token)
            unique.append(token)
    return unique


def _csrf_tokens_match(left: str, right: str) -> bool:
    """Compare CSRF secrets as UTF-8 bytes.

    ``hmac.compare_digest`` on ``str`` raises ``TypeError`` for non-ASCII
    text, which would turn a planted cookie or header into a 500.
    """
    return hmac.compare_digest(left.encode('utf-8'), right.encode('utf-8'))


def csrf_protect(f):
    """Require matching CSRF cookie and header on mutating requests."""

    @wraps(f)
    def decorated(*args, **kwargs):
        header_token = request.headers.get(CSRF_HEADER_NAME)
        if not header_token:
            return error_response(CSRF_INVALID, 403)
        for cookie_token in _csrf_cookie_values():
            if _csrf_tokens_match(cookie_token, header_token):
                return f(*args, **kwargs)
        return error_response(CSRF_INVALID, 403)

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
    token = secrets.token_urlsafe(32)
    response = make_response(jsonify({'csrf_token': token}))
    live_name = csrf_cookie_name()
    response.set_cookie(
        live_name,
        token,
        httponly=True,
        secure=cookie_secure(),
        samesite='Lax',
        path=app_cookie_path(),
    )
    expire_legacy_root_cookie(response, live_name, httponly=True)
    if live_name != LEGACY_CSRF_COOKIE_NAME:
        expire_replaced_cookie(response, LEGACY_CSRF_COOKIE_NAME, httponly=True)
    return response
