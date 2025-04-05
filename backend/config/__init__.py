"""
Configuration package for the Vanilla WebApp Framework.

This package provides centralized configuration management for the application,
including application settings, user preferences, and logging configuration.
"""

from .app_config import AppConfig, app_config
from .user_config import UserConfig, user_config
from .logging_config import setup_logging

__all__ = [
    'AppConfig',
    'app_config',
    'UserConfig',
    'user_config',
    'setup_logging'
] 