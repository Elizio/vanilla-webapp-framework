"""
Main application module — dev entrypoint.
"""
from . import app
from .config.app_config import app_config
from .config.logging_config import setup_logging

setup_logging(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app_config.DEBUG)
