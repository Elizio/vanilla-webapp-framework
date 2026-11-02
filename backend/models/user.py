"""SQLAlchemy User model for password and OAuth accounts."""

from sqlalchemy import Boolean, Column, DateTime, Integer, String, UniqueConstraint
from ..db_repository.database import db


class User(db.Base):
    """
    User model representing application users.

    Attributes:
        id (int): Primary key, unique identifier for the user
        username (str): Unique username for login (max 80 chars)
        password_hash (str): Hashed password (max 255 chars), null for OAuth-only users
        email (str): Optional unique email (normalized lower/trim; NULLs allowed)
        oauth_provider (str): OAuth provider name (google, facebook)
        oauth_id (str): Provider-specific user id
        token_version (int): Server-side JWT generation; must match claim ``tv``
        email_verified (bool): True after a verify token is consumed or Google verified
        email_verified_at (datetime): When the address was verified
        verification_exempt (bool): Pre-migration (and unconfigured-signup) accounts
    """

    __tablename__ = 'users'
    __table_args__ = (
        UniqueConstraint('oauth_provider', 'oauth_id', name='uq_oauth'),
        UniqueConstraint('email', name='uq_users_email'),
    )

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    oauth_provider = Column(String(20), nullable=True)
    oauth_id = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    token_version = Column(Integer, nullable=False, default=0, server_default='0')
    email_verified = Column(Boolean, nullable=False, default=False, server_default='0')
    email_verified_at = Column(DateTime, nullable=True)
    verification_exempt = Column(
        Boolean, nullable=False, default=False, server_default='0'
    )

    def __repr__(self) -> str:
        """String representation of the User model."""
        return f'<User {self.username}>'
