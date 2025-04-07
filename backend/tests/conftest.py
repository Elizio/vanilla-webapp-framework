"""
Pytest configuration and fixtures.
"""
import pytest
from .. import create_app, db
import os

@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    """Set environment variables for testing."""
    os.environ["APP_PROFILE"] = "testing"
    yield
    # Clean up
    if "APP_PROFILE" in os.environ:
        del os.environ["APP_PROFILE"]

@pytest.fixture
def test_app():
    """Create a test Flask application."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['DATABASE_URI'] = 'sqlite:///:memory:'
    return app

@pytest.fixture
def test_client(test_app):
    """Create a test client."""
    return test_app.test_client()

@pytest.fixture
def test_db():
    """Create a test database."""
    db.init_db()
    yield db
    db.close() 