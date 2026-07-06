"""Database engine, session factory, and migration helpers."""
import os

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

from ..config.app_config import AppConfig, load_env_file


class Database:
    """SQLAlchemy engine and scoped session singleton."""

    _instance = None
    _engine = None
    _session_factory = None
    _Session = None
    Base = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._engine is not None:
            return

        load_env_file()
        cfg = AppConfig.get_instance()
        database_url = cfg.SQLALCHEMY_DATABASE_URI

        self._engine = create_engine(
            database_url,
            echo=cfg.APP_PROFILE == 'development',
            connect_args=(
                {'check_same_thread': False}
                if database_url.startswith('sqlite')
                else {}
            ),
        )
        self._session_factory = sessionmaker(bind=self._engine)
        self._Session = scoped_session(self._session_factory)
        self.Base = declarative_base()
        self.Base.query = self._Session.query_property()

    @property
    def engine(self):
        return self._engine

    @property
    def session(self):
        return self._Session()

    def init_db(self):
        """Initialize database by creating all tables."""
        self.Base.metadata.create_all(self._engine)

    def close(self):
        """Close all database connections."""
        if self._Session:
            self._Session.remove()
        if self._engine:
            self._engine.dispose()


db = Database()
db_session = db.session


def init_db():
    """Initialize the database."""
    db.init_db()


def _alembic_config():
    from alembic.config import Config

    backend_dir = os.path.dirname(os.path.dirname(__file__))
    return Config(os.path.join(backend_dir, 'alembic.ini'))


def run_migrations():
    """Run Alembic migrations to head."""
    from alembic import command

    command.upgrade(_alembic_config(), 'head')


def bootstrap_dev_database():
    """Create or upgrade a development database, including legacy schemas."""
    from alembic import command

    alembic_cfg = _alembic_config()
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()

    if 'alembic_version' in tables:
        command.upgrade(alembic_cfg, 'head')
        return

    if 'users' not in tables:
        db.init_db()
        command.stamp(alembic_cfg, 'head')
        return

    user_columns = {column['name'] for column in inspector.get_columns('users')}
    if 'oauth_provider' not in user_columns:
        command.stamp(alembic_cfg, '001')
        command.upgrade(alembic_cfg, 'head')
        return

    command.stamp(alembic_cfg, 'head')
