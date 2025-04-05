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
            # Project folder structure
            self.project_folder = os.getenv(
                'PROJECT_FOLDER', 
                str(Path.home() / 'project_folder')
            )
            self.log_folder = str(Path(self.project_folder) / 'logs')
            
            self._initialized = True

    @classmethod
    def get_instance(cls):
        """Get the singleton instance."""
        return cls()

    def to_dict(self):
        """Convert configuration to dictionary."""
        return {
            'project_folder': self.project_folder,
            'log_folder': self.log_folder
        }

# Create a global configuration instance
user_config = UserConfig.get_instance() 