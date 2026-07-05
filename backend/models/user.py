from sqlalchemy import Boolean, Column, Integer, String, UniqueConstraint
from ..db_repository.database import db


class User(db.Base):
    """
    User model representing application users.

    Attributes:
        id (int): Primary key, unique identifier for the user
        username (str): Unique username for login (max 80 chars)
        password_hash (str): Hashed password (max 128 chars), null for OAuth-only users
        email (str): Optional email from OAuth provider (not unique)
        oauth_provider (str): OAuth provider name (google, facebook)
        oauth_id (str): Provider-specific user id
    """
    __tablename__ = 'users'
    __table_args__ = (
        UniqueConstraint('oauth_provider', 'oauth_id', name='uq_oauth'),
    )

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=True)
    email = Column(String(255), nullable=True)
    oauth_provider = Column(String(20), nullable=True)
    oauth_id = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        """String representation of the User model."""
        return f'<User {self.username}>'
