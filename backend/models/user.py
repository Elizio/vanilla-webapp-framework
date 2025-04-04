from sqlalchemy import Column, Integer, String
from typing import Optional
from ..db_repository.database import db

class User(db.Base):
    """
    User model representing application users.
    
    Attributes:
        id (int): Primary key, unique identifier for the user
        username (str): Unique username for login (max 80 chars)
        password_hash (str): Hashed password (max 128 chars)
    """
    __tablename__ = 'users'

    id: int = Column(Integer, primary_key=True)
    username: str = Column(String(80), unique=True, nullable=False)
    password_hash: str = Column(String(128), nullable=False)

    def __repr__(self) -> str:
        """String representation of the User model."""
        return f'<User {self.username}>'

    @property
    def is_active(self) -> bool:
        """Check if the user account is active."""
        return True  # Add more complex logic if needed 