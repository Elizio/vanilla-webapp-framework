"""Logging must not crash on a missing or unwritable dir, and must not duplicate."""
import logging
from pathlib import Path

from flask import Flask

from backend.config.logging_config import resolve_log_file_path, setup_logging
from backend.config.user_config import UserConfig, reset_user_config_for_tests


def test_resolve_log_file_path_does_not_double_logs_segment():
    """PROJECT_FOLDER=/data/logs must write /data/logs/app.log, not .../logs/logs."""
    assert resolve_log_file_path('/data/logs') == Path('/data/logs/app.log')
    assert resolve_log_file_path('/data') == Path('/data/logs/app.log')


def test_user_config_log_folder_does_not_double_logs(monkeypatch):
    """UserConfig must not nest /logs under a folder already named logs."""
    monkeypatch.setenv('PROJECT_FOLDER', '/data/logs')
    reset_user_config_for_tests()
    try:
        assert UserConfig.get_instance().log_folder == '/data/logs'
    finally:
        monkeypatch.setenv('PROJECT_FOLDER', '/tmp/vanilla-webapp')
        reset_user_config_for_tests()


def test_setup_logging_absent_dir_does_not_create_or_raise(tmp_path, monkeypatch):
    """Default (stdout) logging must not mkdir or crash when the log dir is absent."""
    missing = tmp_path / 'does-not-exist'
    monkeypatch.setenv('PROJECT_FOLDER', str(missing))
    monkeypatch.delenv('LOG_TO_FILE', raising=False)
    monkeypatch.delenv('LOG_FILE', raising=False)
    reset_user_config_for_tests()

    app = Flask(__name__)
    setup_logging(app)
    app.logger.info('hello from absent dir')

    assert not missing.exists()


def test_setup_logging_unwritable_dir_does_not_raise(tmp_path, monkeypatch):
    """File logging must not crash the app when the log dir cannot be created."""
    monkeypatch.setenv('PROJECT_FOLDER', str(tmp_path / 'locked'))
    monkeypatch.setenv('LOG_TO_FILE', '1')
    reset_user_config_for_tests()

    def boom(self, *args, **kwargs):
        raise OSError('permission denied')

    monkeypatch.setattr(Path, 'mkdir', boom)

    app = Flask(__name__)
    setup_logging(app)
    app.logger.info('hello from unwritable dir')


def test_setup_logging_called_twice_adds_one_handler():
    """setup_logging must be idempotent so app.py + create_app do not duplicate."""
    app = Flask('vwf-logging-idempotent')
    setup_logging(app)
    setup_logging(app)
    ours = [
        handler
        for handler in app.logger.handlers
        if getattr(handler, '_vwf_handler', False)
    ]
    assert len(ours) == 1


def test_file_logging_writes_without_doubled_logs_path(tmp_path, monkeypatch):
    """LOG_TO_FILE with PROJECT_FOLDER=.../logs writes app.log in that folder."""
    project = tmp_path / 'data' / 'logs'
    project.mkdir(parents=True)
    monkeypatch.setenv('PROJECT_FOLDER', str(project))
    monkeypatch.setenv('LOG_TO_FILE', '1')
    reset_user_config_for_tests()

    app = Flask('vwf-logging-file')
    setup_logging(app)
    app.logger.info('file hello')
    for handler in app.logger.handlers:
        handler.flush()

    log_file = project / 'app.log'
    assert log_file.is_file()
    assert not (project / 'logs').exists()
    assert 'file hello' in log_file.read_text()

    monkeypatch.setenv('PROJECT_FOLDER', '/tmp/vanilla-webapp')
    monkeypatch.delenv('LOG_TO_FILE', raising=False)
    reset_user_config_for_tests()


def test_setup_logging_defaults_to_stream(monkeypatch, tmp_path):
    """Without LOG_TO_FILE / LOG_FILE, logging goes to a stream (stdout/stderr)."""
    monkeypatch.setenv('PROJECT_FOLDER', str(tmp_path / 'logs'))
    monkeypatch.delenv('LOG_TO_FILE', raising=False)
    monkeypatch.delenv('LOG_FILE', raising=False)
    reset_user_config_for_tests()

    app = Flask('vwf-logging-stream-default')
    setup_logging(app)
    ours = [
        handler
        for handler in app.logger.handlers
        if getattr(handler, '_vwf_handler', False)
    ]
    assert len(ours) == 1
    assert isinstance(ours[0], logging.StreamHandler)
    assert not isinstance(ours[0], logging.FileHandler)
