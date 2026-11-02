"""OAuth 2.0 social login via Authlib (Google, Facebook)."""

import re
from urllib.parse import quote

from authlib.integrations.flask_client import OAuth
from flask import Blueprint, Flask, current_app, jsonify, redirect

from ..db_repository.database import db_session
from ..models.user import User
from .auth import user_may_authenticate
from .error_codes import ACCOUNT_INACTIVE, PROVIDER_NOT_CONFIGURED
from .session_auth import set_auth_cookie

oauth = OAuth()
oauth_bp = Blueprint('oauth', __name__)

# Pin authorize, token, and /me to one currently supported Graph API version.
FACEBOOK_GRAPH_API_VERSION = 'v26.0'

_ENABLED_PROVIDERS = set()
_oauth_app = None


def register_oauth_clients(app: Flask) -> None:
    """Register OAuth provider clients for configured credentials.

    A provider is enabled only when both its client id and secret are set.
    Missing credentials leave that provider off (login/callback 404). In the
    production profile, an enabled provider with an empty
    ``OAUTH_REDIRECT_BASE`` logs a warning and does not crash.
    """
    global _ENABLED_PROVIDERS, _oauth_app
    if _oauth_app is not app:
        oauth.init_app(app)
        _oauth_app = app
    _ENABLED_PROVIDERS = set()

    cfg = app.config
    if cfg.get('GOOGLE_CLIENT_ID') and cfg.get('GOOGLE_CLIENT_SECRET'):
        oauth.register(
            name='google',
            overwrite=True,
            client_id=cfg['GOOGLE_CLIENT_ID'],
            client_secret=cfg['GOOGLE_CLIENT_SECRET'],
            server_metadata_url=(
                'https://accounts.google.com/.well-known/openid-configuration'
            ),
            client_kwargs={'scope': 'openid email profile'},
        )
        _ENABLED_PROVIDERS.add('google')

    if cfg.get('FACEBOOK_CLIENT_ID') and cfg.get('FACEBOOK_CLIENT_SECRET'):
        version = FACEBOOK_GRAPH_API_VERSION
        oauth.register(
            name='facebook',
            overwrite=True,
            client_id=cfg['FACEBOOK_CLIENT_ID'],
            client_secret=cfg['FACEBOOK_CLIENT_SECRET'],
            authorize_url=f'https://www.facebook.com/{version}/dialog/oauth',
            access_token_url=(
                f'https://graph.facebook.com/{version}/oauth/access_token'
            ),
            api_base_url='https://graph.facebook.com/',
            client_kwargs={'scope': 'email'},
        )
        _ENABLED_PROVIDERS.add('facebook')

    _warn_if_missing_production_redirect_base(app)


def enabled_providers() -> list[str]:
    """Return enabled provider keys in sorted order."""
    return sorted(_ENABLED_PROVIDERS)


def _warn_if_missing_production_redirect_base(app: Flask) -> None:
    """Warn when production OAuth is on but ``OAUTH_REDIRECT_BASE`` is empty."""
    if app.config.get('APP_PROFILE') != 'production':
        return
    if not _ENABLED_PROVIDERS:
        return
    base = (app.config.get('OAUTH_REDIRECT_BASE') or '').strip()
    if base:
        return
    app.logger.warning(
        'OAUTH_REDIRECT_BASE is empty while OAuth providers are enabled '
        'in production; callback URLs will be relative. Set it to the '
        'public app URL including any subpath '
        '(for example https://dsfor.fun/vanilla-webapp-framework).'
    )


def _redirect_uri(provider):
    base = current_app.config.get('OAUTH_REDIRECT_BASE', '').rstrip('/')
    return f'{base}/api/auth/{provider}/callback'


def _frontend_redirect(**query):
    frontend = current_app.config.get('FRONTEND_URL', '/').rstrip('/')
    parts = '&'.join(f'{k}={quote(str(v))}' for k, v in query.items())
    url = f'{frontend}/?{parts}' if parts else frontend
    return redirect(url)


def _generate_username(email, name, provider, oauth_id):
    if email:
        base = email.split('@')[0]
    elif name:
        base = re.sub(r'[^\w]', '', name.lower())
    else:
        base = f'{provider}_{oauth_id[:8]}'

    base = re.sub(r'[^\w]', '', base)[:40] or f'{provider}_user'
    username = base
    suffix = 1
    while db_session.query(User).filter_by(username=username).first():
        username = f'{base}{suffix}'
        suffix += 1
    return username


def find_or_create_oauth_user(
    provider: str,
    oauth_id: str,
    email: str | None,
    name: str | None,
    email_verified: bool = False,
) -> User:
    """Find an existing OAuth user or create a new OAuth-only account.

    Email linking attaches the provider identity to a local (password)
    account with the same email. That happens only when the provider
    asserts the address is verified.

    Google userinfo includes ``email_verified``. Facebook Graph
    ``me?fields=id,name,email`` has no verified flag, so Facebook never
    links by email: it always creates or reuses its own provider account
    (the same fallback used for an unverified Google email). ``users.email``
    is not unique.

    Args:
        provider: OAuth provider key (``google`` or ``facebook``).
        oauth_id: Provider-specific user id.
        email: Email from the provider profile, if any.
        name: Display name from the provider profile, if any.
        email_verified: True only when the provider asserts verification.

    Returns:
        The matched or newly created User.
    """
    user = (
        db_session.query(User)
        .filter_by(
            oauth_provider=provider,
            oauth_id=oauth_id,
        )
        .first()
    )
    if user:
        return user

    # Google: link only when userinfo.email_verified is True.
    # Facebook: never link by email (no verified signal).
    if provider == 'google' and email and email_verified:
        existing = db_session.query(User).filter_by(email=email).first()
        if existing and existing.oauth_provider is None:
            existing.oauth_provider = provider
            existing.oauth_id = oauth_id
            try:
                db_session.commit()
            except Exception:
                db_session.rollback()
                raise
            return existing

    user = User(
        username=_generate_username(email, name, provider, oauth_id),
        email=email,
        oauth_provider=provider,
        oauth_id=oauth_id,
        password_hash=None,
    )
    try:
        db_session.add(user)
        db_session.commit()
    except Exception:
        db_session.rollback()
        raise
    return user


def _fetch_userinfo(client, provider, token):
    """Return oauth_id, email, name, and email_verified for a provider."""
    if provider == 'google':
        userinfo = token.get('userinfo')
        if not userinfo:
            resp = client.get('userinfo', token=token)
            userinfo = resp.json()
        return {
            'oauth_id': userinfo['sub'],
            'email': userinfo.get('email'),
            'name': userinfo.get('name'),
            'email_verified': userinfo.get('email_verified') is True,
        }

    if provider == 'facebook':
        # Graph has no email-verified flag on me?fields=id,name,email.
        resp = client.get(
            f'{FACEBOOK_GRAPH_API_VERSION}/me?fields=id,name,email',
            token=token,
        )
        data = resp.json()
        return {
            'oauth_id': data['id'],
            'email': data.get('email'),
            'name': data.get('name'),
            'email_verified': False,
        }

    raise ValueError(f'Unsupported provider: {provider}')


@oauth_bp.route('/api/auth/providers', methods=['GET'])
def list_providers():
    """
    List enabled OAuth providers.
    ---
    tags:
      - Authentication
    responses:
      200:
        description: List of enabled provider names
    """
    return jsonify(enabled_providers())


@oauth_bp.route('/api/auth/<provider>/login', methods=['GET'])
def oauth_login(provider):
    """
    Start OAuth login for a social provider.
    ---
    tags:
      - Authentication
    parameters:
      - in: path
        name: provider
        required: true
        type: string
        enum: [google, facebook]
    responses:
      302:
        description: Redirect to provider authorization page
      404:
        description: Provider not configured
    """
    if provider not in _ENABLED_PROVIDERS:
        return jsonify({'code': PROVIDER_NOT_CONFIGURED}), 404

    client = oauth.create_client(provider)
    return client.authorize_redirect(_redirect_uri(provider))


@oauth_bp.route('/api/auth/<provider>/callback', methods=['GET'])
def oauth_callback(provider):
    """
    OAuth callback — exchange code, create or find user, set auth cookie.
    ---
    tags:
      - Authentication
    parameters:
      - in: path
        name: provider
        required: true
        type: string
        enum: [google, facebook]
    responses:
      302:
        description: >-
          Redirect to FRONTEND_URL with an httpOnly auth cookie
          (`?auth=success` or `?auth_error=CODE`)
      404:
        description: Provider not configured
    """
    if provider not in _ENABLED_PROVIDERS:
        return jsonify({'code': PROVIDER_NOT_CONFIGURED}), 404

    client = oauth.create_client(provider)
    try:
        token = client.authorize_access_token()
        profile = _fetch_userinfo(client, provider, token)
        user = find_or_create_oauth_user(
            provider,
            profile['oauth_id'],
            profile.get('email'),
            profile.get('name'),
            email_verified=profile.get('email_verified') is True,
        )
        if not user_may_authenticate(user):
            return _frontend_redirect(auth_error=ACCOUNT_INACTIVE)
        response = _frontend_redirect(auth='success')
        set_auth_cookie(response, user.id, user.token_version)
        return response
    except Exception as exc:
        current_app.logger.error('OAuth callback failed for %s: %s', provider, exc)
        return _frontend_redirect(auth_error='AUTH_FAILED')
