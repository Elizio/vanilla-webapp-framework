"""
Application configuration management.

Loads environment variables once from the project-root ``.env`` in non-production
profiles, then exposes them through a singleton ``AppConfig``.
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_ENV_LOADED = False


def load_env_file() -> None:
    """Load ``.env`` into ``os.environ`` once (skipped in production).

    Resolution order for the file path:
    1. ``ENV_FILE`` environment variable (absolute or relative path)
    2. ``<project_root>/.env``

    Existing process environment variables are never overwritten
    (``override=False``). In production, only real platform env vars are used.
    """
    global _ENV_LOADED
    if _ENV_LOADED:
        return

    profile = os.getenv('APP_PROFILE', 'development')
    if profile != 'production':
        env_path = Path(os.getenv('ENV_FILE', str(PROJECT_ROOT / '.env')))
        if env_path.is_file():
            load_dotenv(dotenv_path=env_path, override=False)

    _ENV_LOADED = True


class AppConfig:
    """Application configuration singleton backed by ``os.environ``."""

    _instance: Optional['AppConfig'] = None
    _initialized: bool = False

    def __new__(cls) -> 'AppConfig':
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            load_env_file()
            self._initialize_config()
            self._initialized = True

    def _initialize_config(self) -> None:
        """Initialize configuration values from environment variables."""
        self.APP_PROFILE = os.getenv('APP_PROFILE', 'development').strip("'\"")
        self.FLASK_APP = os.getenv('FLASK_APP', 'backend.app')
        self.DEBUG = self.APP_PROFILE == 'development'
        self.TESTING = self.APP_PROFILE == 'testing'

        self.SECRET_KEY = os.getenv('FLASK_SECRET')
        self.JWT_SECRET_KEY = os.getenv('JWT_SECRET')

        if self.TESTING and (not self.SECRET_KEY or not self.JWT_SECRET_KEY):
            self.SECRET_KEY = self.SECRET_KEY or 'test-flask-secret-key'
            self.JWT_SECRET_KEY = self.JWT_SECRET_KEY or 'test-jwt-secret-key'
        elif not self.SECRET_KEY or not self.JWT_SECRET_KEY:
            raise ValueError(
                'Security keys (FLASK_SECRET, JWT_SECRET) must be set in environment'
            )

        self.SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
        if self.TESTING and not self.SQLALCHEMY_DATABASE_URI:
            self.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        elif not self.SQLALCHEMY_DATABASE_URI:
            raise ValueError('DATABASE_URI must be set in environment')

        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        self.API_HOST = os.getenv('API_HOST', 'localhost:5000')

        self.GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
        self.GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
        self.FACEBOOK_CLIENT_ID = os.getenv('FACEBOOK_CLIENT_ID')
        self.FACEBOOK_CLIENT_SECRET = os.getenv('FACEBOOK_CLIENT_SECRET')

        default_frontend = (
            'http://localhost:5173'
            if self.APP_PROFILE in ('development', 'testing')
            else '/'
        )
        self.FRONTEND_URL = os.getenv('FRONTEND_URL', default_frontend)
        self.OAUTH_REDIRECT_BASE = os.getenv(
            'OAUTH_REDIRECT_BASE',
            'http://localhost:5173'
            if self.APP_PROFILE in ('development', 'testing')
            else '',
        )

        cors_raw = os.getenv('CORS_ORIGINS', '').strip()
        if cors_raw:
            self.CORS_ORIGINS = [
                origin.strip().rstrip('/')
                for origin in cors_raw.split(',')
                if origin.strip()
            ]
        else:
            self.CORS_ORIGINS = [self.FRONTEND_URL.rstrip('/')]

        seo_mode = os.getenv('SEO_MODE', 'auth-first').strip("'\"")
        self.SEO_MODE = (
            seo_mode if seo_mode in ('auth-first', 'public-first') else 'auth-first'
        )

        swagger_enabled = os.getenv('SWAGGER_ENABLED', '').lower() in (
            '1',
            'true',
            'yes',
        )
        self.SWAGGER_ENABLED = swagger_enabled or self.APP_PROFILE != 'production'

        self.BILLING_PROVIDER = os.getenv('BILLING_PROVIDER', 'lemon_squeezy')
        self.LEMON_SQUEEZY_API_KEY = os.getenv('LEMON_SQUEEZY_API_KEY')
        self.LEMON_SQUEEZY_STORE_ID = os.getenv('LEMON_SQUEEZY_STORE_ID')
        self.LEMON_SQUEEZY_WEBHOOK_SECRET = os.getenv('LEMON_SQUEEZY_WEBHOOK_SECRET')
        self.LEMON_SQUEEZY_VARIANT_ID_SUPPORTER = os.getenv(
            'LEMON_SQUEEZY_VARIANT_ID_SUPPORTER'
        )

        self.SWAGGER_CONFIG = {
            'headers': [],
            'specs': [{
                'endpoint': 'apispec',
                'route': '/apispec.json',
                'rule_filter': lambda rule: True,
                'model_filter': lambda tag: True,
            }],
            'static_url_path': '/flasgger_static',
            'swagger_ui': True,
            'specs_route': '/docs',
            'title': 'Vanilla WebApp API',
            'version': '1.0.0',
            'description': 'API documentation for Vanilla WebApp Framework',
            'termsOfService': '',
            'contact': {'email': ''},
            'license': '',
            'licenseUrl': '',
            'schemes': ['http', 'https'],
            'host': self.API_HOST,
            'basePath': '/',
            'consumes': ['application/json'],
            'produces': ['application/json'],
            'securityDefinitions': {
                'Bearer': {
                    'type': 'apiKey',
                    'name': 'Authorization',
                    'in': 'header',
                }
            },
        }

    @classmethod
    def get_instance(cls) -> 'AppConfig':
        """Return the singleton configuration instance."""
        return cls()

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to a dict, excluding secrets."""
        return {
            'APP_PROFILE': self.APP_PROFILE,
            'FLASK_APP': self.FLASK_APP,
            'DEBUG': self.DEBUG,
            'TESTING': self.TESTING,
            'API_HOST': self.API_HOST,
            'SQLALCHEMY_DATABASE_URI': self.SQLALCHEMY_DATABASE_URI,
            'SQLALCHEMY_TRACK_MODIFICATIONS': self.SQLALCHEMY_TRACK_MODIFICATIONS,
            'SEO_MODE': self.SEO_MODE,
        }


app_config = AppConfig.get_instance()


def reset_app_config_for_tests() -> None:
    """Clear cached config so tests can re-read ``os.environ``.

    For use in tests only — do not call in application code.
    """
    global _ENV_LOADED, app_config
    AppConfig._instance = None
    AppConfig._initialized = False
    _ENV_LOADED = False
    app_config = AppConfig.get_instance()
