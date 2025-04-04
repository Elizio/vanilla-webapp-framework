"""
Application-level configuration settings.
"""
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv, set_key

class AppConfig:
    """Base application configuration."""
    # Flask configuration
    FLASK_APP = os.environ.get('FLASK_APP', 'backend.app')
    EXECUTION_PROFILE = os.environ.get('EXECUTION_PROFILE', 'development')
    
    # Database configuration
    DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Swagger configuration
    SWAGGER_CONFIG = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs",
        "title": "Vanilla WebApp API",
        "version": "1.0.0",
        "description": "API documentation for Vanilla WebApp Framework",
        "termsOfService": "",
        "contact": {
            "email": ""
        },
        "license": "",
        "licenseUrl": "",
        "schemes": ["http", "https"],
        "host": os.environ.get('API_HOST', 'localhost:5000'),
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

class DevelopmentAppConfig(AppConfig):
    """Development application configuration."""
    DEBUG = True
    TESTING = False

class ProductionAppConfig(AppConfig):
    """Production application configuration."""
    DEBUG = False
    TESTING = False

class TestingAppConfig(AppConfig):
    """Testing application configuration."""
    TESTING = True
    DEBUG = True
    DATABASE_URI = 'sqlite:///:memory:'

# Application configuration dictionary
app_config = {
    'development': DevelopmentAppConfig,
    'testing': TestingAppConfig,
    'production': ProductionAppConfig,
}

def load_env_variables():
    """Loads configuration variables from a *.env file into the OS
    Should be called directly, before from_environment_variables is called"""
    print("Number of arguments:", len(sys.argv), "arguments")
    print("Argument List:", str(sys.argv))
    
    # Handle jupyter notebook environment
    if 'ipykernel_launcher' in sys.argv[0]:
        sys.argv = ['.\\app.py', '--APP_PROFILE',
                    'development', '--ENV_FILE', os.path.join(sys.path[0], "../.env")]
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--APP_PROFILE', help='APP_PROFILE: name of the environment i.e. PRD, DEV, QA, DOCKER')
    parser.add_argument('--ENV_FILE',
                        help='ENV_FILE: path to the file where its defined the variables of the environment')

    if len(sys.argv) > 1:
        args = parser.parse_args()
        app_profile = args.APP_PROFILE
        env_file = args.ENV_FILE
        if app_profile is None or env_file is None:
            parser.print_help()
            sys.exit(1)
        else:
            set_key(env_file, "EXECUTION_PROFILE", app_profile)
            load_dotenv(dotenv_path=env_file)
    else:
        # Default to development if no arguments provided
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        if os.path.exists(env_file):
            load_dotenv(dotenv_path=env_file)
        else:
            print("Warning: No .env file found. Using default development settings.")

def get_environment_profile():
    """Get the current environment from EXECUTION_PROFILE variable."""
    return os.getenv('APP_PROFILE', 'development')

# Load environment variables at module import
load_env_variables() 