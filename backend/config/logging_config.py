"""Logging configuration: stdout by default, optional rotating file."""

from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from .user_config import UserConfig


def resolve_log_file_path(project_folder: str) -> Path:
    """Return the app.log path without doubling a trailing ``logs`` segment.

    A ``PROJECT_FOLDER`` whose last segment is already ``logs`` writes
    ``app.log`` in that folder, not a nested ``logs/logs`` path.

    Args:
        project_folder: ``PROJECT_FOLDER`` value (for example a project
            root, or a directory already named ``logs``).

    Returns:
        Path to ``app.log`` under the resolved log directory.
    """
    folder = Path(project_folder)
    if folder.name == 'logs':
        return folder / 'app.log'
    return folder / 'logs' / 'app.log'


def _file_logging_requested() -> bool:
    """Return True when file logging is explicitly enabled."""
    if os.getenv('LOG_FILE'):
        return True
    return os.getenv('LOG_TO_FILE', '').strip().lower() in ('1', 'true', 'yes')


def _build_handler() -> logging.Handler:
    """Create a stream handler, or a file handler when explicitly requested."""
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    handler: logging.Handler | None = None
    if _file_logging_requested():
        configured = os.getenv('LOG_FILE')
        path = (
            Path(configured)
            if configured
            else resolve_log_file_path(UserConfig.get_instance().project_folder)
        )
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            handler = RotatingFileHandler(
                path,
                maxBytes=1_048_576,
                backupCount=10,
            )
        except OSError:
            handler = None

    if handler is None:
        handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    handler._vwf_handler = True  # type: ignore[attr-defined]
    return handler


def setup_logging(app: Any) -> None:
    """Configure application logging once.

    Defaults to stdout/stderr so a missing or unwritable ``PROJECT_FOLDER``
    cannot crash import. File logging is opt-in via ``LOG_TO_FILE`` or
    ``LOG_FILE``.

    Args:
        app: Flask application instance.
    """
    logger = app.logger
    if getattr(app, '_vwf_logging_configured', False):
        return
    if any(getattr(handler, '_vwf_handler', False) for handler in logger.handlers):
        app._vwf_logging_configured = True
        return

    handler = _build_handler()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    app._vwf_logging_configured = True
    logger.info('Application startup')
