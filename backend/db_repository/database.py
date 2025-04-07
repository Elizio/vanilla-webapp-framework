from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
import os

class Database:
    _instance = None
    _engine = None
    _session_factory = None
    _Session = None
    Base = None  # Make Base class-level

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._engine is None:
            # Get database URL from environment or use SQLite
            database_url = os.environ.get('DATABASE_URI', 'sqlite:///app.db')
            
            # Force SQLite for testing
            if os.environ.get('APP_PROFILE') == 'testing':
                database_url = 'sqlite:///:memory:'
                print("Using in-memory SQLite database for testing (from database.py)")
            
            # Create engine with appropriate configuration
            self._engine = create_engine(
                database_url,
                echo=os.environ.get('APP_PROFILE') == 'development',
                connect_args={'check_same_thread': False} if database_url.startswith('sqlite') else {}
            )
            
            # Create session factory
            self._session_factory = sessionmaker(bind=self._engine)
            
            # Create thread-safe session
            self._Session = scoped_session(self._session_factory)
            
            # Create declarative base
            self.Base = declarative_base()
            
            # Add query property to all models
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

# Create global database instance
db = Database()

# Create global session
db_session = db.session

def init_db():
    """Initialize the database."""
    db.init_db() 