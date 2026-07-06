"""SPA static serving and global error handlers."""
import os
from flask import Response, current_app, request, send_from_directory, abort
from werkzeug.exceptions import HTTPException

from .api.error_codes import NOT_FOUND, INTERNAL_ERROR, error_response


def build_robots_txt(seo_mode: str) -> str:
    """Build robots.txt body from fork SEO_MODE.

    Args:
        seo_mode: ``auth-first`` or ``public-first``.

    Returns:
        robots.txt file contents.
    """
    if seo_mode == 'public-first':
        return '\n'.join([
            'User-agent: *',
            'Allow: /',
            'Disallow: /api/',
            'Disallow: /docs',
            'Disallow: /apispec.json',
            'Disallow: /flasgger_static/',
            '',
        ])

    return '\n'.join([
        'User-agent: *',
        'Disallow: /',
        '',
    ])


def register_web_routes(app):
    """Register SPA static serving and error handlers on the Flask app."""

    @app.after_request
    def set_security_headers(response):
        """Apply baseline security headers to every response."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        if current_app.config.get('APP_PROFILE') == 'production':
            response.headers['Strict-Transport-Security'] = (
                'max-age=31536000; includeSubDomains'
            )
        return response

    @app.route('/robots.txt')
    def robots_txt():
        """Serve crawl directives driven by SEO_MODE."""
        seo_mode = current_app.config.get('SEO_MODE', os.getenv('SEO_MODE', 'auth-first'))
        body = build_robots_txt(seo_mode)
        return Response(body, mimetype='text/plain')

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_spa(path):
        """Serve SPA static assets; fallback to index.html for client-side routes."""
        if path.startswith(('api/', 'docs', 'apispec.json', 'flasgger_static')):
            abort(404)

        static_folder = app.static_folder
        if path:
            full_path = os.path.join(static_folder, path)
            if os.path.isfile(full_path):
                return send_from_directory(static_folder, path)

        response = send_from_directory(static_folder, 'index.html')
        response.headers['Cache-Control'] = 'no-cache'
        return response

    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.error(f'Page not found: {request.url}')
        return error_response(NOT_FOUND, 404)

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Server Error: {error}')
        return error_response(INTERNAL_ERROR, 500)

    @app.errorhandler(HTTPException)
    def http_exception(error):
        if error.code == 404:
            return error_response(NOT_FOUND, 404)
        if error.code and error.code >= 500:
            return error_response(INTERNAL_ERROR, error.code)
        return error_response(NOT_FOUND, error.code or 400)
