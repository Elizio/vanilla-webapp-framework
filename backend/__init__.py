"""
Backend package for the Vanilla WebApp Framework.
"""

import os
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from .db_repository.database import db, db_session, init_db, run_migrations
from .config import AppConfig, UserConfig, setup_logging


def create_app():
    """Create and configure the Flask application."""
    profile = os.getenv('APP_PROFILE', 'development')
    static_dir = 'static' if profile == 'production' else '../frontend/src'

    app = Flask(__name__, static_folder=static_dir)

    CORS(app)

    app.config.from_object(AppConfig.get_instance())

    user_config = UserConfig.get_instance()
    app.config.update(user_config.to_dict())

    setup_logging(app)

    swagger = Swagger(app, config=app.config['SWAGGER_CONFIG'])

    from .api.auth import auth_bp
    from .api.routes import api_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db._Session.remove()

    from .web_routes import register_web_routes
    register_web_routes(app)

    if profile == 'production':
        run_migrations()
    else:
        init_db()

    return app


app = create_app()


__all__ = [
    'app',
    'db',
    'db_session',
    'init_db',
    'create_app',
]
