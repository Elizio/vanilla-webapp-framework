"""Root pytest configuration — set test env before any backend imports."""

import os

os.environ["APP_PROFILE"] = "testing"
os.environ["FLASK_SECRET"] = "test-flask-secret-key"
os.environ["JWT_SECRET"] = "test-jwt-secret-key"
# File SQLite so the email worker thread shares the schema.
os.environ["DATABASE_URI"] = "sqlite:////tmp/vanilla-webapp-pytest.db"
os.environ["PROJECT_FOLDER"] = "/tmp/vanilla-webapp"
