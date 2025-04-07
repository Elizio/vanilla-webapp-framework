"""
Main application module.
"""
from flask import render_template, jsonify, request
from . import app
from .config.app_config import app_config
from .config.logging_config import setup_logging

# Setup logging
setup_logging(app)

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app_config.DEBUG) 