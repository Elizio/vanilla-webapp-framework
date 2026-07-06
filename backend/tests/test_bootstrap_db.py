"""Tests for development database bootstrap."""
import os
from sqlalchemy import create_engine, inspect
from alembic import command
from alembic.config import Config


def test_bootstrap_dev_database_upgrades_legacy_schema(tmp_path, monkeypatch):
    """Legacy users table without OAuth columns is upgraded on bootstrap."""
    db_path = tmp_path / 'legacy.db'
    engine = create_engine(f'sqlite:///{db_path}')
    with engine.begin() as conn:
        conn.exec_driver_sql(
            'CREATE TABLE users ('
            'id INTEGER PRIMARY KEY, '
            'username VARCHAR(80) NOT NULL UNIQUE, '
            'password_hash VARCHAR(128) NOT NULL)'
        )

    monkeypatch.setenv('DATABASE_URI', f'sqlite:///{db_path}')
    monkeypatch.setenv('APP_PROFILE', 'development')

    from backend.config.app_config import reset_app_config_for_tests
    from backend.db_repository import database as db_module

    reset_app_config_for_tests()

    db_module.Database._instance = None
    db_module.db = db_module.Database()
    db_module.db_session = db_module.db.session

    db_module.bootstrap_dev_database()

    columns = {column['name'] for column in inspect(db_module.db.engine).get_columns('users')}
    assert {'email', 'oauth_provider', 'oauth_id'}.issubset(columns)

    backend_dir = os.path.join(os.path.dirname(__file__), '..')
    alembic_cfg = Config(os.path.join(backend_dir, 'alembic.ini'))
    alembic_cfg.set_main_option('sqlalchemy.url', f'sqlite:///{db_path}')
    command.upgrade(alembic_cfg, 'head')
