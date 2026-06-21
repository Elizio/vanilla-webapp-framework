"""Tests for SEO crawl directives."""
import pytest

from backend import create_app, db
from backend.web_routes import build_robots_txt


@pytest.mark.parametrize(
    ('seo_mode', 'expected_lines'),
    [
        ('auth-first', ['User-agent: *', 'Disallow: /']),
        (
            'public-first',
            [
                'User-agent: *',
                'Allow: /',
                'Disallow: /api/',
                'Disallow: /docs',
            ],
        ),
    ],
)
def test_build_robots_txt(seo_mode, expected_lines):
    body = build_robots_txt(seo_mode)
    for line in expected_lines:
        assert line in body


def _production_client(tmp_path, monkeypatch, seo_mode):
    static_dir = tmp_path / 'static'
    static_dir.mkdir()
    (static_dir / 'index.html').write_text('<html><body>production</body></html>')

    monkeypatch.setenv('APP_PROFILE', 'production')
    monkeypatch.setenv('SEO_MODE', seo_mode)
    monkeypatch.setattr(
        'backend.db_repository.database.run_migrations',
        lambda: db.init_db(),
    )

    app = create_app()
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
    app.config['SEO_MODE'] = seo_mode
    app.static_folder = str(static_dir)
    return app.test_client()


def test_robots_txt_auth_first(tmp_path, monkeypatch):
    client = _production_client(tmp_path, monkeypatch, 'auth-first')
    response = client.get('/robots.txt')

    assert response.status_code == 200
    assert response.mimetype == 'text/plain'
    assert b'Disallow: /' in response.data
    assert b'Allow: /' not in response.data


def test_robots_txt_public_first(tmp_path, monkeypatch):
    client = _production_client(tmp_path, monkeypatch, 'public-first')
    response = client.get('/robots.txt')

    assert response.status_code == 200
    assert b'Allow: /' in response.data
    assert b'Disallow: /api/' in response.data
