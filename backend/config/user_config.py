"""
User-specific configuration settings.
"""
import os
from pathlib import Path

class UserConfig:
    """Base user configuration singleton."""
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserConfig, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            # Default values
            self.database_uri = os.getenv(
                'DATABASE_URI',
                'sqlite:///app.db'
            )
            self.project_folder = os.getenv(
                'PROJECT_FOLDER', 
                str(Path.home() / 'Projects')
            )
            self.log_folder = str(Path(self.project_folder) / 'logs')
            self._initialized = True

    @classmethod
    def get_instance(cls):
        """Get the singleton instance."""
        return cls()
