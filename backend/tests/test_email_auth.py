"""Email verification, password reset, and unconfigured SMTP mode."""

from __future__ import annotations

import re
from datetime import timedelta
from typing import Any
from unittest.mock import MagicMock

import jwt
from flask import Flask
from flask.testing import FlaskClient
from pytest import MonkeyPatch
from werkzeug.security import generate_password_hash
from werkzeug.test import TestResponse

from backend.api.auth_tokens import (
    PURPOSE_RESET,
    PURPOSE_VERIFY,
    hash_auth_token,
    issue_auth_token,
)
from backend.api.jwt_utils import JWT_ALGORITHM
from backend.api.refresh_tokens import utc_now
from backend.db_repository.database import db_session
from backend.email.console import clear_outbox, get_outbox
from backend.email.service import is_email_configured
from backend.models.auth_token import AuthToken
from backend.models.refresh_token import RefreshToken
from backend.models.user import User
from backend.tests.conftest import csrf_headers, login_user, register_user


def _enable_console_email(
    app: Flask, *, require_verified: bool = True, app_name: str = 'TestApp'
) -> None:
    """Turn on the console backend for one Flask app."""
    app.config['EMAIL_BACKEND'] = 'console'
    app.config['FRONTEND_URL'] = 'http://localhost:5173'
    app.config['APP_NAME'] = app_name
    app.config['EMAIL_FROM'] = 'noreply@example.com'
    app.config['REQUIRE_EMAIL_VERIFIED'] = require_verified
    clear_outbox()


def _json(response: TestResponse) -> dict[str, Any]:
    """Return the JSON object body, failing the test if it is missing."""
    payload = response.get_json()
    assert isinstance(payload, dict)
    return payload


def _token_from_outbox(purpose: str) -> str:
    """Extract the raw action token from the latest console message."""
    messages = [item for item in get_outbox() if item.purpose == purpose]
    assert messages, f'no console email for purpose={purpose}'
    key = 'verify_token' if purpose == PURPOSE_VERIFY else 'reset_token'
    match = re.search(rf'{key}=([^&\s]+)', messages[-1].body)
    assert match, messages[-1].body
    return match.group(1)


def test_unconfigured_register_and_login_match_today(
    test_client: FlaskClient, test_db: object, test_app: Flask
) -> None:
    """With no SMTP env vars, sign-up logs in and login is not blocked."""
    assert test_app.config.get('EMAIL_BACKEND') in ('', None)
    response = register_user(test_client, username='plain', password='testpass8')
    assert response.status_code == 201
    assert response.json['code'] == 'USER_CREATED'
    assert response.json['authenticated'] is True
    assert test_client.get_cookie('auth_token') is not None
    logout = test_client.post('/api/auth/logout', headers=csrf_headers(test_client))
    assert logout.status_code == 200
    login = login_user(test_client, username='plain', password='testpass8')
    assert login.status_code == 200
    assert login.json['authenticated'] is True


def test_unconfigured_password_reset_unavailable(
    test_client: FlaskClient, test_db: object, test_app: Flask
) -> None:
    """Forgot/reset return a clear error when email sending is off."""
    headers = csrf_headers(test_client)
    forgot = test_client.post(
        '/api/auth/password/forgot',
        json={'email': 'anyone@example.com'},
        headers=headers,
    )
    assert forgot.status_code == 503
    assert _json(forgot)['code'] == 'EMAIL_NOT_CONFIGURED'
    reset = test_client.post(
        '/api/auth/password/reset',
        json={'token': 'nope', 'password': 'newpass88'},
        headers=csrf_headers(test_client),
    )
    assert reset.status_code == 503
    assert _json(reset)['code'] == 'EMAIL_NOT_CONFIGURED'
    resend = test_client.post(
        '/api/auth/verify-email/resend',
        json={'email': 'anyone@example.com'},
        headers=csrf_headers(test_client),
    )
    assert resend.status_code == 503
    caps = test_client.get('/api/auth/capabilities')
    assert caps.status_code == 200
    assert caps.json == {
        'email_configured': False,
        'password_reset': False,
        'email_verification': False,
    }


def test_unconfigured_create_app_does_not_crash(monkeypatch: MonkeyPatch) -> None:
    """EMAIL_BACKEND=smtp with no SMTP vars must not fail startup."""
    from backend.config.app_config import reset_app_config_for_tests
    from backend import create_app

    monkeypatch.setenv('APP_PROFILE', 'testing')
    monkeypatch.setenv('EMAIL_BACKEND', 'smtp')
    monkeypatch.setenv('FRONTEND_URL', '/')
    reset_app_config_for_tests()
    app = create_app()
    assert app.config['EMAIL_BACKEND'] == 'smtp'
    with app.app_context():
        assert is_email_configured() is False
    monkeypatch.setenv('EMAIL_BACKEND', '')
    monkeypatch.delenv('FRONTEND_URL', raising=False)
    reset_app_config_for_tests()


def test_smtp_relative_frontend_url_is_unconfigured(
    test_client: FlaskClient, test_db: object, test_app: Flask
) -> None:
    """SMTP plus a relative FRONTEND_URL stays disabled (no startup crash)."""
    test_app.config['EMAIL_BACKEND'] = 'smtp'
    test_app.config['SMTP_HOST'] = 'smtp.resend.com'
    test_app.config['SMTP_PORT'] = 465
    test_app.config['SMTP_USERNAME'] = 'resend'
    test_app.config['SMTP_PASSWORD'] = 're_test_key'
    test_app.config['SMTP_SECURITY'] = 'ssl'
    test_app.config['EMAIL_FROM'] = 'no-reply@dsfor.fun'
    test_app.config['FRONTEND_URL'] = '/'
    with test_app.app_context():
        assert is_email_configured() is False
    forgot = test_client.post(
        '/api/auth/password/forgot',
        json={'email': 'a@b.com'},
        headers=csrf_headers(test_client),
    )
    assert forgot.status_code == 503
    assert _json(forgot)['code'] == 'EMAIL_NOT_CONFIGURED'


def test_register_requires_email_and_does_not_set_cookie(
    test_client: FlaskClient, test_db: object, test_app: Flask
) -> None:
    _enable_console_email(test_app)
    response = test_client.post(
        '/api/register',
        json={
            'username': 'newbie',
            'password': 'testpass8',
            'email': 'New@Example.COM',
            'locale': 'en',
        },
        headers=csrf_headers(test_client),
    )
    assert response.status_code == 201
    assert _json(response)['code'] == 'USER_CREATED'
    assert _json(response)['authenticated'] is False
    assert test_client.get_cookie('auth_token') is None
    user = User.query.filter_by(username='newbie').first()
    assert user.email == 'new@example.com'
    assert user.email_verified is False
    assert user.verification_exempt is False
    assert len(get_outbox()) == 1
    message = get_outbox()[0]
    assert 'TestApp' in message.subject
    assert 'TestApp' in message.body
    assert 'TestApp' in message.from_addr
    assert message.purpose == PURPOSE_VERIFY
    assert 'http://localhost:5173/?verify_token=' in message.body


def test_register_email_exists(
    test_client: FlaskClient, test_db: object, test_app: Flask
) -> None:
    _enable_console_email(test_app)
    payload = {
        'username': 'first',
        'password': 'testpass8',
        'email': 'dup@example.com',
    }
    assert (
        test_client.post(
            '/api/register', json=payload, headers=csrf_headers(test_client)
        ).status_code
        == 201
    )
    second = test_client.post(
        '/api/register',
        json={
            'username': 'second',
            'password': 'testpass8',
            'email': 'DUP@example.com',
        },
        headers=csrf_headers(test_client),
    )
    assert second.status_code == 400
    assert _json(second)['code'] == 'EMAIL_EXISTS'


def test_login_unverified_after_correct_password(
    test_client: FlaskClient, test_db: object, test_app: Flask
) -> None:
    _enable_console_email(test_app)
    test_client.post(
        '/api/register',
        json={
            'username': 'locked',
            'password': 'testpass8',
            'email': 'locked@example.com',
        },
        headers=csrf_headers(test_client),
    )
    wrong = login_user(test_client, username='locked', password='wrongpass')
    assert wrong.status_code == 401
    assert wrong.json['code'] == 'INVALID_CREDENTIALS'
    right = login_user(test_client, username='locked', password='testpass8')
    assert right.status_code == 403
    assert right.json['code'] == 'EMAIL_NOT_VERIFIED'


def test_verify_logs_in_and_is_single_use(
    test_client: FlaskClient, test_db: object, test_app: Flask
) -> None:
    _enable_console_email(test_app)
    test_client.post(
        '/api/register',
        json={
            'username': 'verifyme',
            'password': 'testpass8',
            'email': 'verifyme@example.com',
        },
        headers=csrf_headers(test_client),
    )
    token = _token_from_outbox(PURPOSE_VERIFY)
    first = test_client.post(
        '/api/auth/verify-email',
        json={'token': token},
        headers=csrf_headers(test_client),
    )
    assert first.status_code == 200
    assert _json(first)['code'] == 'EMAIL_VERIFIED'
    assert _json(first)['authenticated'] is True
    session = test_client.get('/api/auth/session')
    assert _json(session)['authenticated'] is True
    assert _json(session)['email_verified'] is True
    reuse = test_client.post(
        '/api/auth/verify-email',
        json={'token': token},
        headers=csrf_headers(test_client),
    )
    assert reuse.status_code == 400
    assert _json(reuse)['code'] == 'TOKEN_INVALID_OR_EXPIRED'
    unknown = test_client.post(
        '/api/auth/verify-email',
        json={'token': 'not-a-real-token'},
        headers=csrf_headers(test_client),
    )
    assert unknown.status_code == 400
    assert _json(unknown)['code'] == 'TOKEN_INVALID_OR_EXPIRED'


def test_expired_verify_token_rejected(
    test_client: FlaskClient, test_db: object, test_app: Flask
) -> None:
    _enable_console_email(test_app)
    user = User(
        username='expuser',
        password_hash=generate_password_hash('testpass8'),
        email='exp@example.com',
        email_verified=False,
    )
    db_session.add(user)
    db_session.commit()
    raw = issue_auth_token(int(user.id), PURPOSE_VERIFY)
    db_session.query(AuthToken).filter_by(token_hash=hash_auth_token(raw)).update(
        {AuthToken.expires_at: utc_now() - timedelta(hours=2)},
        synchronize_session=False,
    )
    db_session.commit()
    db_session.expire_all()
    response = test_client.post(
        '/api/auth/verify-email',
        json={'token': raw},
        headers=csrf_headers(test_client),
    )
    assert response.status_code == 400
    assert _json(response)['code'] == 'TOKEN_INVALID_OR_EXPIRED'


def test_preexisting_exempt_user_can_login(
    test_client: FlaskClient, test_db: object, test_app: Flask
) -> None:
    _enable_console_email(test_app)
    user = User(
        username='legacy',
        password_hash=generate_password_hash('testpass8'),
        email='legacy@example.com',
        email_verified=False,
        verification_exempt=True,
    )
    db_session.add(user)
    db_session.commit()
    response = login_user(test_client, username='legacy', password='testpass8')
    assert response.status_code == 200
    assert response.json['authenticated'] is True


def test_forgot_and_resend_same_for_known_and_unknown(
    test_client: FlaskClient, test_db: object, test_app: Flask
) -> None:
    _enable_console_email(test_app)
    test_client.post(
        '/api/register',
        json={
            'username': 'known',
            'password': 'testpass8',
            'email': 'known@example.com',
        },
        headers=csrf_headers(test_client),
    )
    clear_outbox()
    headers = csrf_headers(test_client)
    known = test_client.post(
        '/api/auth/password/forgot',
        json={'email': 'known@example.com'},
        headers=headers,
    )
    unknown = test_client.post(
        '/api/auth/password/forgot',
        json={'email': 'missing@example.com'},
        headers=csrf_headers(test_client),
    )
    assert known.status_code == unknown.status_code == 202
    assert known.json == unknown.json == {'code': 'EMAIL_ACCEPTED'}
    resend_known = test_client.post(
        '/api/auth/verify-email/resend',
        json={'email': 'known@example.com'},
        headers=csrf_headers(test_client),
    )
    resend_unknown = test_client.post(
        '/api/auth/verify-email/resend',
        json={'email': 'missing@example.com'},
        headers=csrf_headers(test_client),
    )
    assert resend_known.status_code == resend_unknown.status_code == 202
    assert resend_known.json == resend_unknown.json


def test_send_cooldown_skips_second_mail(
    test_client: FlaskClient, test_db: object, test_app: Flask
) -> None:
    _enable_console_email(test_app)
    test_client.post(
        '/api/register',
        json={
            'username': 'cool',
            'password': 'testpass8',
            'email': 'cool@example.com',
        },
        headers=csrf_headers(test_client),
    )
    assert len(get_outbox()) == 1
    test_client.post(
        '/api/auth/verify-email/resend',
        json={'email': 'cool@example.com'},
        headers=csrf_headers(test_client),
    )
    assert len(get_outbox()) == 1


def test_password_reset_revokes_sessions_and_other_tokens(
    test_client: FlaskClient, test_db: object, test_app: Flask
) -> None:
    _enable_console_email(test_app)
    test_client.post(
        '/api/register',
        json={
            'username': 'resetme',
            'password': 'oldpass88',
            'email': 'resetme@example.com',
        },
        headers=csrf_headers(test_client),
    )
    user = User.query.filter_by(username='resetme').one()
    user_id = int(user.id)
    db_session.query(User).filter_by(username='resetme').update(
        {User.email_verified: True},
        synchronize_session=False,
    )
    db_session.commit()
    db_session.expire_all()
    login = login_user(test_client, username='resetme', password='oldpass88')
    assert login.status_code == 200
    access = test_client.get_cookie('auth_token')
    assert access is not None
    old_jwt = access.value
    test_client.post(
        '/api/auth/password/forgot',
        json={'email': 'resetme@example.com'},
        headers=csrf_headers(test_client),
    )
    extra = issue_auth_token(user_id, PURPOSE_RESET)
    token = _token_from_outbox(PURPOSE_RESET)
    reset = test_client.post(
        '/api/auth/password/reset',
        json={'token': token, 'password': 'newpass88'},
        headers=csrf_headers(test_client),
    )
    assert reset.status_code == 200
    assert _json(reset)['code'] == 'PASSWORD_RESET'
    reused = test_client.post(
        '/api/auth/password/reset',
        json={'token': extra, 'password': 'another99'},
        headers=csrf_headers(test_client),
    )
    assert reused.status_code == 400
    payload = jwt.decode(old_jwt, 'test-jwt-secret-key', algorithms=[JWT_ALGORITHM])
    user = User.query.filter_by(username='resetme').first()
    assert payload['tv'] != user.token_version
    refresh_rows = db_session.query(RefreshToken).filter_by(user_id=user_id).all()
    assert refresh_rows
    assert all(row.revoked_at is not None for row in refresh_rows)
    stale = test_client.get('/api/data', headers={'Authorization': f'Bearer {old_jwt}'})
    assert stale.status_code == 401
    old_login = login_user(test_client, username='resetme', password='oldpass88')
    assert old_login.status_code == 401
    new_login = login_user(test_client, username='resetme', password='newpass88')
    assert new_login.status_code == 200


def test_oauth_only_user_sets_password_via_reset(
    test_client: FlaskClient, test_db: object, test_app: Flask
) -> None:
    _enable_console_email(test_app)
    user = User(
        username='oauthonly',
        password_hash=None,
        email='oauth@example.com',
        oauth_provider='google',
        oauth_id='sub-oauth',
        email_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    test_client.post(
        '/api/auth/password/forgot',
        json={'email': 'oauth@example.com'},
        headers=csrf_headers(test_client),
    )
    token = _token_from_outbox(PURPOSE_RESET)
    reset = test_client.post(
        '/api/auth/password/reset',
        json={'token': token, 'password': 'firstpass'},
        headers=csrf_headers(test_client),
    )
    assert reset.status_code == 200
    login = login_user(test_client, username='oauthonly', password='firstpass')
    assert login.status_code == 200


def test_email_links_include_subpath(
    test_client: FlaskClient, test_db: object, test_app: Flask
) -> None:
    _enable_console_email(test_app)
    test_app.config['FRONTEND_URL'] = 'https://dsfor.fun/vanilla-webapp-framework'
    test_client.post(
        '/api/register',
        json={
            'username': 'subpath',
            'password': 'testpass8',
            'email': 'subpath@example.com',
        },
        headers=csrf_headers(test_client),
    )
    body = get_outbox()[0].body
    assert 'https://dsfor.fun/vanilla-webapp-framework/?verify_token=' in body


def test_custom_app_name_in_email(
    test_client: FlaskClient, test_db: object, test_app: Flask
) -> None:
    _enable_console_email(test_app, app_name='Acme Fork')
    test_client.post(
        '/api/register',
        json={
            'username': 'acme',
            'password': 'testpass8',
            'email': 'acme@example.com',
            'locale': 'pt-BR',
        },
        headers=csrf_headers(test_client),
    )
    message = get_outbox()[0]
    assert 'Acme Fork' in message.subject
    assert 'Acme Fork' in message.body
    assert 'Acme Fork' in message.from_addr
    assert 'Confirme seu e-mail' in message.subject


def test_add_email_sends_verification(
    test_client: FlaskClient, test_db: object, test_app: Flask
) -> None:
    _enable_console_email(test_app)
    user = User(
        username='banner',
        password_hash=generate_password_hash('testpass8'),
        email=None,
        verification_exempt=True,
    )
    db_session.add(user)
    db_session.commit()
    login = login_user(test_client, username='banner', password='testpass8')
    assert login.status_code == 200
    added = test_client.post(
        '/api/auth/email',
        json={'email': 'banner@example.com'},
        headers=csrf_headers(test_client),
    )
    assert added.status_code == 202
    assert get_outbox()[0].purpose == PURPOSE_VERIFY
    db_session.refresh(user)
    assert user.email == 'banner@example.com'


def test_smtp_backend_uses_starttls_or_ssl(
    test_client: FlaskClient,
    test_db: object,
    test_app: Flask,
    monkeypatch: MonkeyPatch,
) -> None:
    """stdlib smtplib is used; secrets are not logged."""
    from backend.email.smtp import SmtpEmailBackend
    from backend.email.backend import OutboundEmail

    smtp_ssl = MagicMock()
    instance = MagicMock()
    smtp_ssl.return_value = instance
    monkeypatch.setattr('backend.email.smtp.smtplib.SMTP_SSL', smtp_ssl)

    test_app.config['EMAIL_BACKEND'] = 'smtp'
    test_app.config['SMTP_HOST'] = 'smtp.resend.com'
    test_app.config['SMTP_PORT'] = 465
    test_app.config['SMTP_USERNAME'] = 'resend'
    test_app.config['SMTP_PASSWORD'] = 're_secret_key'
    test_app.config['SMTP_SECURITY'] = 'ssl'
    test_app.config['EMAIL_FROM'] = 'no-reply@dsfor.fun'
    test_app.config['FRONTEND_URL'] = 'https://dsfor.fun/vanilla-webapp-framework'
    test_app.config['APP_PROFILE'] = 'testing'
    with test_app.app_context():
        assert is_email_configured() is True
        SmtpEmailBackend().send(
            OutboundEmail(
                to='user@example.com',
                subject='Confirm your email for vanilla-webapp-framework',
                body='https://dsfor.fun/vanilla-webapp-framework/?verify_token=secret-token',
                from_addr='vanilla-webapp-framework <no-reply@dsfor.fun>',
                purpose='verify',
            )
        )
    smtp_ssl.assert_called_once()
    instance.login.assert_called_once_with('resend', 're_secret_key')
    instance.sendmail.assert_called_once()
    sent_payload = instance.sendmail.call_args[0][2]
    assert 'secret-token' in sent_payload
    instance.quit.assert_called_once()

    smtp_plain = MagicMock()
    starttls_client = MagicMock()
    smtp_plain.return_value = starttls_client
    monkeypatch.setattr('backend.email.smtp.smtplib.SMTP', smtp_plain)
    test_app.config['SMTP_SECURITY'] = 'starttls'
    test_app.config['SMTP_PORT'] = 587
    with test_app.app_context():
        SmtpEmailBackend().send(
            OutboundEmail(
                to='user@example.com',
                subject='Reset',
                body='reset link',
                from_addr='vanilla-webapp-framework <no-reply@dsfor.fun>',
                purpose='reset',
            )
        )
    smtp_plain.assert_called_once()
    starttls_client.starttls.assert_called_once()
    starttls_client.login.assert_called_once_with('resend', 're_secret_key')


def test_console_does_not_log_body_in_production(
    test_client: FlaskClient,
    test_db: object,
    test_app: Flask,
    monkeypatch: MonkeyPatch,
) -> None:
    from backend.email.console import ConsoleEmailBackend
    from backend.email.backend import OutboundEmail
    from backend.email import console as console_mod

    recorded: list[str] = []

    def _info(msg: str, *args: object, **_kwargs: object) -> None:
        recorded.append(msg % args if args else msg)

    monkeypatch.setattr(console_mod.logger, 'info', _info)
    test_app.config['APP_PROFILE'] = 'production'
    with test_app.app_context():
        ConsoleEmailBackend().send(
            OutboundEmail(
                to='user@example.com',
                subject='subj',
                body='token=super-secret-token',
                from_addr='app <a@b.c>',
                purpose='verify',
            )
        )
    combined = ' '.join(recorded)
    assert 'super-secret-token' not in combined
    assert 'purpose=verify' in combined
