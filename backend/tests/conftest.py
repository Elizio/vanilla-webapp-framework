"""
Pytest configuration and fixtures.
"""
import os

os.environ["APP_PROFILE"] = "testing"
os.environ["FLASK_SECRET"] = "test-flask-secret-key"
os.environ["JWT_SECRET"] = "test-jwt-secret-key"
os.environ["DATABASE_URI"] = "sqlite:///:memory:"
os.environ["PROJECT_FOLDER"] = "/tmp/vanilla-webapp"

import pytest
from .. import create_app, db


def csrf_headers(client):
    """Return CSRF header after priming the double-submit cookie."""
    response = client.get('/api/csrf')
    token = response.json['csrf_token']
    return {'X-CSRF-Token': token}


def register_user(client, username='testuser', password='testpass8'):
    """Register a user with CSRF protection."""
    return client.post(
        '/api/register',
        json={'username': username, 'password': password},
        headers=csrf_headers(client),
    )


def login_user(client, username='testuser', password='testpass8'):
    """Log in and return the response (session cookie stored on client)."""
    return client.post(
        '/api/login',
        json={'username': username, 'password': password},
        headers=csrf_headers(client),
    )


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    """Ensure test environment variables stay set."""
    os.environ["APP_PROFILE"] = "testing"
    os.environ["FLASK_SECRET"] = "test-flask-secret-key"
    os.environ["JWT_SECRET"] = "test-jwt-secret-key"
    os.environ["DATABASE_URI"] = "sqlite:///:memory:"
    os.environ["PROJECT_FOLDER"] = "/tmp/vanilla-webapp"
    yield


@pytest.fixture
def test_app():
    """Create a test Flask application."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
    return app


@pytest.fixture
def test_client(test_app):
    """Create a test client."""
    return test_app.test_client()


@pytest.fixture
def test_db():
    """Provide a clean schema per test.

    Recreate tables on setup and drop them on teardown. The in-memory SQLite
    engine is intentionally *not* disposed between tests: disposing it drops
    the database held by the single pooled connection, which made schema
    visibility order-dependent across tests.
    """
    db._Session.remove()
    db.Base.metadata.drop_all(db.engine)
    db.init_db()
    yield db
    db._Session.remove()
    db.Base.metadata.drop_all(db.engine)


@pytest.fixture
def production_client(tmp_path, monkeypatch):
    """Flask test client with production profile and temp static folder."""
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    (static_dir / "index.html").write_text("<html><body>production</body></html>")
    (static_dir / "file.txt").write_text("static-file")

    monkeypatch.setenv("APP_PROFILE", "production")
    monkeypatch.setattr(
        "backend.db_repository.database.run_migrations",
        lambda: db.init_db(),
    )

    app = create_app()
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
    app.static_folder = str(static_dir)
    return app.test_client()
