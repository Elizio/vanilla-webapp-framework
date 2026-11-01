"""Tests for the /api/health endpoint."""
from sqlalchemy.exc import SQLAlchemyError

from backend.db_repository.database import db_session


def test_health_ok_includes_version(test_client, test_db, monkeypatch):
    """Health returns 200 with status ok and the APP_VERSION when the DB is up."""
    monkeypatch.setenv('APP_VERSION', 'abc123def')

    response = test_client.get('/api/health')

    assert response.status_code == 200
    assert response.json['status'] == 'ok'
    assert response.json['version'] == 'abc123def'
    assert response.json['db'] == 'ok'


def test_health_version_unknown_when_unset(test_client, test_db, monkeypatch):
    """Health reports version unknown when APP_VERSION is not set."""
    monkeypatch.delenv('APP_VERSION', raising=False)

    response = test_client.get('/api/health')

    assert response.status_code == 200
    assert response.json['status'] == 'ok'
    assert response.json['version'] == 'unknown'


def test_health_returns_503_when_database_fails(test_client, test_db, monkeypatch):
    """Health returns 503 with a non-ok status when the DB session raises."""
    monkeypatch.setenv('APP_VERSION', 'deadbeef')

    def fail_execute(*args, **kwargs):
        raise SQLAlchemyError('simulated db failure')

    monkeypatch.setattr(db_session, 'execute', fail_execute)

    response = test_client.get('/api/health')

    assert response.status_code == 503
    assert response.json['status'] != 'ok'
    assert response.json['version'] == 'deadbeef'
    assert 'simulated db failure' not in str(response.get_json())
    assert 'SQLAlchemy' not in str(response.get_json())
