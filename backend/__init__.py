"""
Backend package for the Vanilla WebApp Framework.
"""

from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

from .config import AppConfig, UserConfig, setup_logging
from .db_repository.database import (
    bootstrap_dev_database,
    db,
    db_session,
    init_db,
    run_migrations,
)


def create_app():
    """Create and configure the Flask application."""
    app_config = AppConfig.get_instance()
    static_dir = (
        'static' if app_config.APP_PROFILE == 'production' else '../frontend/src'
    )

    app = Flask(__name__, static_folder=static_dir)
    app.config.from_object(app_config)

    cors_origins = app.config.get('CORS_ORIGINS') or [app.config.get('FRONTEND_URL')]
    CORS(app, origins=cors_origins, supports_credentials=True)

    user_config = UserConfig.get_instance()
    app.config.update(user_config.to_dict())

    setup_logging(app)

    if app_config.SWAGGER_ENABLED:
        Swagger(app, config=app.config['SWAGGER_CONFIG'])

    from .api.auth import auth_bp
    from .api.routes import api_bp
    from .api.oauth import oauth_bp, register_oauth_clients
    from .api.billing import billing_bp
    from .api.csrf import csrf_bp

    register_oauth_clients(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(oauth_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(csrf_bp)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db._Session.remove()

    from .web_routes import register_web_routes

    register_web_routes(app)

    if app_config.APP_PROFILE == 'production':
        run_migrations()
    elif app_config.APP_PROFILE == 'development':
        bootstrap_dev_database()
    else:
        init_db()

    return app


__all__ = [
    'db',
    'db_session',
    'init_db',
    'create_app',
]
