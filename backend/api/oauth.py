"""OAuth 2.0 social login via Authlib (Google, Facebook)."""
import re
from urllib.parse import quote

from authlib.integrations.flask_client import OAuth
from flask import Blueprint, current_app, jsonify, redirect

from ..db_repository.database import db_session
from ..models.user import User
from .jwt_utils import generate_token

oauth = OAuth()
oauth_bp = Blueprint('oauth', __name__)

_ENABLED_PROVIDERS = set()
_oauth_app = None


def register_oauth_clients(app):
    """Register OAuth provider clients for configured credentials."""
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
        oauth.register(
            name='facebook',
            overwrite=True,
            client_id=cfg['FACEBOOK_CLIENT_ID'],
            client_secret=cfg['FACEBOOK_CLIENT_SECRET'],
            authorize_url='https://www.facebook.com/v19.0/dialog/oauth',
            access_token_url='https://graph.facebook.com/v19.0/oauth/access_token',
            api_base_url='https://graph.facebook.com/',
            client_kwargs={'scope': 'email'},
        )
        _ENABLED_PROVIDERS.add('facebook')


def enabled_providers():
    return sorted(_ENABLED_PROVIDERS)


def _redirect_uri(provider):
    base = current_app.config.get('OAUTH_REDIRECT_BASE', '').rstrip('/')
    return f'{base}/api/auth/{provider}/callback'


def _frontend_redirect(**fragment):
    frontend = current_app.config.get('FRONTEND_URL', '/').rstrip('/')
    parts = '&'.join(f'{k}={quote(str(v))}' for k, v in fragment.items())
    return redirect(f'{frontend}/#{parts}')


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
    while User.query.filter_by(username=username).first():
        username = f'{base}{suffix}'
        suffix += 1
    return username


def find_or_create_oauth_user(provider, oauth_id, email, name):
    """Find user by OAuth identity or create a new OAuth-only account."""
    user = User.query.filter_by(
        oauth_provider=provider,
        oauth_id=oauth_id,
    ).first()
    if user:
        return user

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
    if provider == 'google':
        userinfo = token.get('userinfo')
        if not userinfo:
            resp = client.get('userinfo', token=token)
            userinfo = resp.json()
        return {
            'oauth_id': userinfo['sub'],
            'email': userinfo.get('email'),
            'name': userinfo.get('name'),
        }

    if provider == 'facebook':
        resp = client.get('me?fields=id,name,email', token=token)
        data = resp.json()
        return {
            'oauth_id': data['id'],
            'email': data.get('email'),
            'name': data.get('name'),
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
        return jsonify({'message': 'Provider not configured'}), 404

    client = oauth.create_client(provider)
    return client.authorize_redirect(_redirect_uri(provider))


@oauth_bp.route('/api/auth/<provider>/callback', methods=['GET'])
def oauth_callback(provider):
    """
    OAuth callback — exchange code, create or find user, issue JWT.
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
        description: Redirect to SPA with JWT in URL fragment
      404:
        description: Provider not configured
    """
    if provider not in _ENABLED_PROVIDERS:
        return jsonify({'message': 'Provider not configured'}), 404

    client = oauth.create_client(provider)
    try:
        token = client.authorize_access_token()
        profile = _fetch_userinfo(client, provider, token)
        user = find_or_create_oauth_user(
            provider,
            profile['oauth_id'],
            profile.get('email'),
            profile.get('name'),
        )
        jwt_token = generate_token(user.id)
        return _frontend_redirect(token=jwt_token)
    except Exception as exc:
        current_app.logger.error('OAuth callback failed for %s: %s', provider, exc)
        return _frontend_redirect(auth_error='Authentication failed')
