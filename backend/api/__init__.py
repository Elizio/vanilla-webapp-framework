"""
API module containing all route blueprints.
"""

from .auth import auth_bp
from .routes import api_bp

__all__ = ['auth_bp', 'api_bp'] 