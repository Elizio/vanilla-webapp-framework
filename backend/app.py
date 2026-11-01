"""Main application module — WSGI / flask-run entrypoint."""

from . import create_app
from .config.app_config import app_config

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app_config.DEBUG)
