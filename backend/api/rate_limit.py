"""In-memory rate limiting for auth endpoints."""
import time
from collections import defaultdict
from functools import wraps

from flask import current_app, request

from .error_codes import RATE_LIMIT_EXCEEDED, error_response

_WINDOW_SECONDS = 60
_MAX_REQUESTS = 10
_hits: dict[str, list[float]] = defaultdict(list)


def rate_limit_auth(f):
    """Limit auth endpoints to 10 requests per minute per IP."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if current_app.config.get('TESTING'):
            return f(*args, **kwargs)
        key = request.remote_addr or 'unknown'
        now = time.time()
        cutoff = now - _WINDOW_SECONDS
        _hits[key] = [stamp for stamp in _hits[key] if stamp > cutoff]
        if len(_hits[key]) >= _MAX_REQUESTS:
            return error_response(RATE_LIMIT_EXCEEDED, 429)
        _hits[key].append(now)
        return f(*args, **kwargs)

    return decorated
