"""Factory tests: production no longer migrates; testing still uses create_all."""
from backend.config.app_config import reset_app_config_for_tests


def test_create_app_production_does_not_call_run_migrations(monkeypatch):
    """Prod-profile create_app must not run Alembic (entrypoint migrates once)."""
    monkeypatch.setenv('APP_PROFILE', 'production')
    monkeypatch.setenv('FLASK_SECRET', 'test-flask-secret-key')
    monkeypatch.setenv('JWT_SECRET', 'test-jwt-secret-key')
    monkeypatch.setenv('DATABASE_URI', 'sqlite:///:memory:')
    reset_app_config_for_tests()

    called = []

    def record_migration():
        called.append(True)

    import backend as backend_pkg
    import backend.db_repository.database as db_module

    monkeypatch.setattr(db_module, 'run_migrations', record_migration)
    if hasattr(backend_pkg, 'run_migrations'):
        monkeypatch.setattr(backend_pkg, 'run_migrations', record_migration)

    from backend import create_app

    create_app()
    assert called == []

    monkeypatch.setenv('APP_PROFILE', 'testing')
    reset_app_config_for_tests()


def test_create_app_testing_still_calls_init_db(monkeypatch):
    """The testing profile keeps create_all via init_db()."""
    monkeypatch.setenv('APP_PROFILE', 'testing')
    reset_app_config_for_tests()

    called = []
    monkeypatch.setattr('backend.init_db', lambda: called.append('init_db'))

    from backend import create_app

    create_app()
    assert called == ['init_db']
