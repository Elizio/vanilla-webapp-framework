"""
Pytest configuration and fixtures.
"""

import os

os.environ["APP_PROFILE"] = "testing"
os.environ["FLASK_SECRET"] = "test-flask-secret-key"
os.environ["JWT_SECRET"] = "test-jwt-secret-key"
# File SQLite so the email worker thread shares the schema.
os.environ["DATABASE_URI"] = "sqlite:////tmp/vanilla-webapp-pytest.db"
os.environ["PROJECT_FOLDER"] = "/tmp/vanilla-webapp"

import pytest  # noqa: E402
from .. import create_app, db  # noqa: E402


def live_cookie_name(client, key='AUTH_COOKIE_NAME'):
    """Return a configured cookie name from the client's app.

    Args:
        client: Flask test client.
        key: Config key such as ``AUTH_COOKIE_NAME``.
    """
    return client.application.config[key]


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


def login_user(client, username='testuser', password='testpass8', remember_me=False):
    """Log in and return the response (session cookie stored on client)."""
    return client.post(
        '/api/login',
        json={
            'username': username,
            'password': password,
            'remember_me': remember_me,
        },
        headers=csrf_headers(client),
    )


def refresh_session(client):
    """Rotate the refresh cookie and return the response."""
    return client.post('/api/auth/refresh', headers=csrf_headers(client))


def logout_session(client):
    """Log out via the canonical refresh-cookie path."""
    return client.post('/api/auth/logout', headers=csrf_headers(client))


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    """Ensure test environment variables stay set."""
    os.environ["APP_PROFILE"] = "testing"
    os.environ["FLASK_SECRET"] = "test-flask-secret-key"
    os.environ["JWT_SECRET"] = "test-jwt-secret-key"
    os.environ["DATABASE_URI"] = "sqlite:////tmp/vanilla-webapp-pytest.db"
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

    Recreate tables on setup and drop them on teardown. Do not dispose the
    engine: tests share one process-wide Database singleton, and the email
    worker thread uses the same file SQLite database.
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
