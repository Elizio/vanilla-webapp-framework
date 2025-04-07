"""
Logging configuration for the application.
"""
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
from .user_config import user_config

def setup_logging(app):
    """
    Configure logging for the Flask application.
    
    Args:
        app: Flask application instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path(user_config.log_folder)
    log_dir.mkdir(exist_ok=True)
    
    # Configure file handler
    file_handler = RotatingFileHandler(
        log_dir / 'app.log',
        maxBytes=10240,
        backupCount=10
    )
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    # Configure handler
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Add handler to app logger
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    # Log application startup
    app.logger.info('Application startup') 