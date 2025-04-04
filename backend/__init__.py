"""
Backend package for the Vanilla WebApp Framework.
"""

from flask import Flask, jsonify, request
from flasgger import Swagger
from .db_repository.database import db, db_session, init_db
from .config.app_config import app_config, get_environment_profile
from .config.user_config import UserConfig
from .config.logging_config import setup_logging

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                static_folder='../frontend/public',
                template_folder='../frontend/src/templates')
    
    # Get current environment profile
    env_profile = get_environment_profile()
    
    # Load configurations
    app.config.from_object(app_config[env_profile])
    
    # Get user configuration singleton instance
    user_config = UserConfig.get_instance()
    
    # Update app config with user config values
    app.config['SQLALCHEMY_DATABASE_URI'] = user_config.database_uri
    app.config['PROJECT_FOLDER'] = user_config.project_folder
    app.config['LOG_FOLDER'] = user_config.log_folder
    
    # Configure logging
    setup_logging(app)

    # Swagger configuration
    swagger = Swagger(app, config=app.config['SWAGGER_CONFIG'])

    # Register blueprints
    from .api.auth import auth_bp
    from .api.routes import api_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    # Initialize database
    init_db()

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.error(f'Page not found: {request.url}')
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        app.logger.error(f'Unhandled Exception: {e}')
        return jsonify({'error': 'Internal server error'}), 500

    return app

# Create the application instance
app = create_app()

__all__ = [
    'app',
    'db',
    'db_session',
    'init_db'
] 