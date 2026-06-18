"""Alembic migration smoke test."""
import os
import pytest
from sqlalchemy import create_engine, inspect
from alembic import command
from alembic.config import Config


def test_alembic_upgrade_head(tmp_path):
    db_path = tmp_path / "migrate_test.db"
    os.environ['DATABASE_URI'] = f'sqlite:///{db_path}'

    backend_dir = os.path.join(os.path.dirname(__file__), '..')
    alembic_cfg = Config(os.path.join(backend_dir, 'alembic.ini'))
    command.upgrade(alembic_cfg, 'head')

    engine = create_engine(f'sqlite:///{db_path}')
    tables = inspect(engine).get_table_names()
    assert 'users' in tables
    assert 'alembic_version' in tables
