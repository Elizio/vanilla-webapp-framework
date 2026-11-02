"""Email feature flags, link building, and send helpers."""

from __future__ import annotations

import logging
import os
import re
from concurrent.futures import Future, ThreadPoolExecutor
from email.utils import formataddr
from typing import TYPE_CHECKING, cast
from urllib.parse import urlencode

from flask import Flask, current_app

from .backend import EmailBackend, OutboundEmail
from .console import ConsoleEmailBackend
from .messages import render_email
from .smtp import SmtpEmailBackend

if TYPE_CHECKING:
    from ..models.user import User

logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
SUPPORTED_LOCALES = frozenset({'en', 'pt-BR'})
VERIFY_PURPOSE = 'verify'
RESET_PURPOSE = 'reset'
_EMAIL_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix='email-send')
_PENDING_EMAIL_JOBS: set[Future[None]] = set()


def whitelist_locale(raw: object) -> str:
    """Return a supported locale, defaulting to ``en``.

    Args:
        raw: Request body ``locale`` value.

    Returns:
        ``en`` or ``pt-BR``.
    """
    if not isinstance(raw, str):
        return 'en'
    value = raw.strip()
    if value in SUPPORTED_LOCALES:
        return value
    lowered = value.lower()
    if lowered == 'pt' or lowered.startswith('pt-'):
        return 'pt-BR'
    return 'en'


def normalize_email(raw: object) -> str | None:
    """Return a lowercased, trimmed address, or ``None`` if invalid.

    Args:
        raw: Untyped JSON value.

    Returns:
        Normalized email, or ``None`` when missing or malformed.
    """
    if not isinstance(raw, str):
        return None
    value = raw.strip().lower()
    if not value or len(value) > 255:
        return None
    if _EMAIL_RE.match(value) is None:
        return None
    return value


def _is_absolute_url(url: str) -> bool:
    lowered = url.lower()
    return lowered.startswith('https://') or lowered.startswith('http://')


def _is_production() -> bool:
    """Return True for ``APP_PROFILE=production`` or ``ENV=production``."""
    profile = str(current_app.config.get('APP_PROFILE') or '').strip().lower()
    if profile == 'production':
        return True
    env = str(os.getenv('ENV') or current_app.config.get('ENV') or '').strip()
    return env.lower() == 'production'


def is_email_configured() -> bool:
    """Return True when a backend can send and ``FRONTEND_URL`` is absolute.

    Missing SMTP env vars, a relative ``FRONTEND_URL``, an unknown
    ``EMAIL_BACKEND``, or the console backend in production all count as
    unconfigured. Never raises.

    Returns:
        Whether verification mail and password reset may run.
    """
    try:
        name = str(current_app.config.get('EMAIL_BACKEND') or '').strip().lower()
        frontend = str(current_app.config.get('FRONTEND_URL') or '').strip()
        if not _is_absolute_url(frontend):
            return False
        if name == 'console':
            return not _is_production()
        if name != 'smtp':
            return False
        host = str(current_app.config.get('SMTP_HOST') or '').strip()
        username = str(current_app.config.get('SMTP_USERNAME') or '').strip()
        password = str(current_app.config.get('SMTP_PASSWORD') or '')
        email_from = str(current_app.config.get('EMAIL_FROM') or '').strip()
        if not (host and username and password and email_from):
            return False
        profile = str(current_app.config.get('APP_PROFILE') or '')
        if profile == 'production' and not frontend.lower().startswith('https://'):
            return False
        return True
    except Exception:
        logger.warning('Email configuration check failed; treating as disabled')
        return False


def login_blocked_unverified(user: User) -> bool:
    """Return True when password login must wait for email confirmation.

    Checked only after a correct password. Unconfigured email, a disabled
    ``REQUIRE_EMAIL_VERIFIED`` flag, exempt (pre-migration) accounts,
    already-verified users, and accounts with no email are not blocked.

    Args:
        user: Authenticated user row.

    Returns:
        Whether the login should return ``EMAIL_NOT_VERIFIED``.
    """
    if not is_email_configured():
        return False
    if not bool(current_app.config.get('REQUIRE_EMAIL_VERIFIED', True)):
        return False
    if bool(getattr(user, 'verification_exempt', False)):
        return False
    if bool(getattr(user, 'email_verified', False)):
        return False
    if not getattr(user, 'email', None):
        return False
    return True


def frontend_action_url(action: str, token: str) -> str:
    """Build ``{FRONTEND_URL}/?verify_token=`` or ``/?reset_token=``.

    ``FRONTEND_URL`` already includes the production subpath
    (``https://dsfor.fun/vanilla-webapp-framework``).

    Args:
        action: ``verify`` or ``reset``.
        token: Raw (unhashed) single-use token.

    Returns:
        Absolute URL for the SPA to consume via POST.
    """
    base = str(current_app.config.get('FRONTEND_URL') or '').rstrip('/')
    key = 'verify_token' if action == VERIFY_PURPOSE else 'reset_token'
    return f'{base}/?{urlencode({key: token})}'


def _app_name() -> str:
    name = str(current_app.config.get('APP_NAME') or '').strip()
    return name or 'vanilla-webapp-framework'


def _from_addr() -> str:
    email_from = str(current_app.config.get('EMAIL_FROM') or '').strip()
    if not email_from:
        email_from = 'no-reply@localhost'
    return formataddr((_app_name(), email_from))


def get_email_backend() -> EmailBackend | None:
    """Return the configured backend, or ``None`` when sending is off.

    Returns:
        A console or SMTP backend, or ``None``.
    """
    if not is_email_configured():
        return None
    name = str(current_app.config.get('EMAIL_BACKEND') or '').strip().lower()
    if name == 'console':
        return ConsoleEmailBackend()
    if name == 'smtp':
        return SmtpEmailBackend()
    return None


def _build_message(user: User, purpose: str, locale: str, token: str) -> OutboundEmail:
    link = frontend_action_url(purpose, token)
    subject, body = render_email(purpose, locale, _app_name(), link)
    return OutboundEmail(
        to=str(user.email),
        subject=subject,
        body=body,
        from_addr=_from_addr(),
        purpose=purpose,
    )


def _prepare_message(user: User, purpose: str, locale: str) -> OutboundEmail | None:
    from ..api.auth_tokens import can_send, issue_auth_token

    if not user.email or not is_email_configured():
        return None
    if not can_send(int(user.id), purpose):
        return None
    raw = issue_auth_token(int(user.id), purpose)
    return _build_message(user, purpose, whitelist_locale(locale), raw)


def _send_now(message: OutboundEmail) -> None:
    backend = get_email_backend()
    if backend is None:
        return
    try:
        backend.send(message)
    except Exception:
        logger.exception('Failed to send email purpose=%s', message.purpose)


def send_verification_email(user: User, locale: str = 'en') -> None:
    """Issue a verify token and send the confirmation message.

    No-ops when email is unconfigured, the user has no address, or the
    per-address cooldown is active. Exceptions from the transport are
    logged and swallowed so sign-up still succeeds.

    Args:
        user: Persisted user with a normalized ``email``.
        locale: Whitelisted locale for the template.
    """
    message = _prepare_message(user, VERIFY_PURPOSE, locale)
    if message is not None:
        _send_now(message)


def send_reset_email(user: User, locale: str = 'en') -> None:
    """Issue a reset token and send the password-reset message.

    Args:
        user: Persisted user with a normalized ``email``.
        locale: Whitelisted locale for the template.
    """
    message = _prepare_message(user, RESET_PURPOSE, locale)
    if message is not None:
        _send_now(message)


def wait_for_auth_emails(timeout: float = 5.0) -> None:
    """Block until queued background email jobs finish.

    Args:
        timeout: Seconds to wait for each pending future.
    """
    pending = list(_PENDING_EMAIL_JOBS)
    for future in pending:
        future.result(timeout=timeout)


def queue_auth_email(purpose: str, email: str, locale: str) -> None:
    """Look up ``email`` and enqueue a send off the request thread.

    Known and unknown addresses share this path: one lookup, then one
    bounded-executor job. The worker calls the mailer (or no-ops when
    the address is unknown). Failures log ``purpose`` only.

    Args:
        purpose: ``verify`` or ``reset``.
        email: Normalized recipient.
        locale: Whitelisted locale.
    """
    from ..models.user import User

    user = User.query.filter_by(email=email).first()
    message: OutboundEmail | None = None
    if user is not None and (purpose == RESET_PURPOSE or not bool(user.email_verified)):
        message = _prepare_message(user, purpose, locale)
    _enqueue_outbound_email(message)


def _enqueue_outbound_email(message: OutboundEmail | None) -> None:
    app = cast(Flask, getattr(current_app, '_get_current_object')())
    future = _EMAIL_EXECUTOR.submit(_deliver_queued, app, message)
    _PENDING_EMAIL_JOBS.add(future)
    future.add_done_callback(_PENDING_EMAIL_JOBS.discard)


def _deliver_queued(app: Flask, message: OutboundEmail | None) -> None:
    """Run the mailer on a worker thread; ``message`` is already rendered."""
    with app.app_context():
        if message is None:
            return
        _send_now(message)
