"""Pluggable outbound email: console (dev/tests) and SMTP (Resend).

Named ``mailer`` so this package cannot shadow stdlib ``email`` when
Docker runs ``python /app/backend/container_healthcheck.py``.
"""

from .backend import EmailBackend, OutboundEmail
from .service import (
    frontend_action_url,
    is_email_configured,
    login_blocked_unverified,
    normalize_email,
    send_reset_email,
    send_verification_email,
    whitelist_locale,
)

__all__ = [
    'EmailBackend',
    'OutboundEmail',
    'frontend_action_url',
    'is_email_configured',
    'login_blocked_unverified',
    'normalize_email',
    'send_reset_email',
    'send_verification_email',
    'whitelist_locale',
]
