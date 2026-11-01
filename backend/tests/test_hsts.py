"""HSTS header must not include includeSubDomains or preload."""
from backend import create_app
from backend.config.app_config import reset_app_config_for_tests
from backend.db_repository.database import db


def _production_client(monkeypatch, tmp_path, **env):
    """Build a production-profile test client.

    Args:
        monkeypatch: pytest monkeypatch fixture.
        tmp_path: Temporary directory for a static folder.
        **env: Extra environment variables.
    """
    static_dir = tmp_path / 'static'
    static_dir.mkdir()
    (static_dir / 'index.html').write_text('<html><body>ok</body></html>')

    monkeypatch.setenv('APP_PROFILE', 'production')
    monkeypatch.setenv('FLASK_SECRET', 'test-flask-secret-key')
    monkeypatch.setenv('JWT_SECRET', 'test-jwt-secret-key')
    monkeypatch.setenv('DATABASE_URI', 'sqlite:///:memory:')
    for key, value in env.items():
        if value is None:
            monkeypatch.delenv(key, raising=False)
        else:
            monkeypatch.setenv(key, value)
    reset_app_config_for_tests()

    app = create_app()
    app.config['TESTING'] = True
    app.static_folder = str(static_dir)
    with app.app_context():
        db.init_db()
    return app.test_client()


def test_production_hsts_has_no_include_subdomains(monkeypatch, tmp_path):
    """Prod HSTS is a plain max-age so it can clear a cached includeSubDomains."""
    client = _production_client(monkeypatch, tmp_path)
    response = client.get('/api/health')
    header = response.headers.get('Strict-Transport-Security')
    assert header == 'max-age=31536000'
    assert 'includeSubDomains' not in header
    assert 'preload' not in header.lower()
    monkeypatch.setenv('APP_PROFILE', 'testing')
    reset_app_config_for_tests()


def test_hsts_disabled_when_flag_off(monkeypatch, tmp_path):
    """HSTS_ENABLED=0 removes the header entirely."""
    client = _production_client(monkeypatch, tmp_path, HSTS_ENABLED='0')
    response = client.get('/api/health')
    assert 'Strict-Transport-Security' not in response.headers
    monkeypatch.setenv('APP_PROFILE', 'testing')
    reset_app_config_for_tests()


def test_testing_profile_does_not_send_hsts(monkeypatch):
    """Non-production profiles never send HSTS."""
    monkeypatch.delenv('HSTS_ENABLED', raising=False)
    monkeypatch.setenv('APP_PROFILE', 'testing')
    reset_app_config_for_tests()
    app = create_app()
    app.config['TESTING'] = True
    response = app.test_client().get('/api/health')
    assert 'Strict-Transport-Security' not in response.headers
