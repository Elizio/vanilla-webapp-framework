"""
Application configuration management.

This module provides a centralized configuration management system that handles
all environment variables and application settings. It implements a singleton pattern
to ensure consistent configuration across the application.
"""
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv, set_key

class AppConfig:
    """
    Application configuration singleton that manages all environment variables
    and application settings.
    """
    _instance: Optional['AppConfig'] = None
    _initialized: bool = False

    def __new__(cls) -> 'AppConfig':
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            self._load_environment()
            self._initialize_config()
            self._initialized = True

    def _load_environment(self) -> None:
        """Load environment variables from .env file and command line arguments."""
        # Handle jupyter notebook environment
        if 'ipykernel_launcher' in sys.argv[0]:
            sys.argv = ['.\\app.py', '--APP_PROFILE',
                       'development', '--ENV_FILE', os.path.join(sys.path[0], "../.env")]
        
        parser = argparse.ArgumentParser(description='Application configuration')
        parser.add_argument('--APP_PROFILE', 
                          help='Environment profile (development, testing, production)')
        parser.add_argument('--ENV_FILE',
                          help='Path to the .env file')

        args = parser.parse_args()
        
        # Load environment file
        env_file = args.ENV_FILE or os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        if os.path.exists(env_file):
            load_dotenv(dotenv_path=env_file)
            if args.APP_PROFILE:
                set_key(env_file, "APP_PROFILE", args.APP_PROFILE)
        else:
            print("Warning: No .env file found. Using default settings.")

    def _initialize_config(self) -> None:
        """Initialize configuration values from environment variables."""
        # Environment
        self.APP_PROFILE = os.getenv('APP_PROFILE', 'development')
        
        # Flask configuration
        self.FLASK_APP = os.getenv('FLASK_APP', 'backend.app')
        self.DEBUG = self.APP_PROFILE == 'development'
        self.TESTING = self.APP_PROFILE == 'testing'
        
        # Security configuration
        self.SECRET_KEY = os.getenv('FLASK_SECRET')
        self.JWT_SECRET_KEY = os.getenv('JWT_SECRET')
        
        # In testing mode, use default test keys if not provided
        if self.TESTING and (not self.SECRET_KEY or not self.JWT_SECRET_KEY):
            self.SECRET_KEY = self.SECRET_KEY or 'test-flask-secret-key'
            self.JWT_SECRET_KEY = self.JWT_SECRET_KEY or 'test-jwt-secret-key'
            print("Using default test security keys.")
        elif not self.SECRET_KEY or not self.JWT_SECRET_KEY:
            raise ValueError("Security keys (FLASK_SECRET, JWT_SECRET) must be set in environment")
        
        # Database configuration
        self.SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
        
        # In testing mode, use SQLite in-memory database if not provided
        if self.TESTING and not self.SQLALCHEMY_DATABASE_URI:
            self.SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
            print("Using in-memory SQLite database for testing.")
        elif not self.SQLALCHEMY_DATABASE_URI:
            raise ValueError("DATABASE_URI must be set in environment")
            
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        
        # API configuration
        self.API_HOST = os.getenv('API_HOST', 'localhost:5000')
        
        # Swagger configuration
        self.SWAGGER_CONFIG = {
            "headers": [],
            "specs": [{
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }],
            "static_url_path": "/flasgger_static",
            "swagger_ui": True,
            "specs_route": "/docs",
            "title": "Vanilla WebApp API",
            "version": "1.0.0",
            "description": "API documentation for Vanilla WebApp Framework",
            "termsOfService": "",
            "contact": {"email": ""},
            "license": "",
            "licenseUrl": "",
            "schemes": ["http", "https"],
            "host": self.API_HOST,
            "basePath": "/",
            "consumes": ["application/json"],
            "produces": ["application/json"],
            "securityDefinitions": {
                "Bearer": {
                    "type": "apiKey",
                    "name": "Authorization",
                    "in": "header"
                }
            }
        }

    @classmethod
    def get_instance(cls) -> 'AppConfig':
        """Get the singleton instance of the configuration."""
        return cls()

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary, excluding sensitive information."""
        return {
            'APP_PROFILE': self.APP_PROFILE,
            'FLASK_APP': self.FLASK_APP,
            'DEBUG': self.DEBUG,
            'TESTING': self.TESTING,
            'API_HOST': self.API_HOST,
            'SQLALCHEMY_DATABASE_URI': self.SQLALCHEMY_DATABASE_URI,
            'SQLALCHEMY_TRACK_MODIFICATIONS': self.SQLALCHEMY_TRACK_MODIFICATIONS,
        }

# Create a global configuration instance
app_config = AppConfig.get_instance() 