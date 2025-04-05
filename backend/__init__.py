"""
Backend package for the Vanilla WebApp Framework.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flasgger import Swagger
from .db_repository.database import db, db_session, init_db
from .config import AppConfig, UserConfig, setup_logging

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                static_folder='../frontend/public',
                template_folder='../frontend/src/templates')
    
    # Enable CORS
    CORS(app)
    
    # Load configurations
    app.config.from_object(AppConfig.get_instance())
    
    # Get user configuration singleton instance
    user_config = UserConfig.get_instance()
    
    # Update app config with user config values
    app.config.update(user_config.to_dict())
    
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

    return app

# Create the application instance
app = create_app()

__all__ = [
    'app',
    'db',
    'db_session',
    'init_db'
] 