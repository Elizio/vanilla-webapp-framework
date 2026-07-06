"""Root pytest configuration — set test env before any backend imports."""
import os

os.environ["APP_PROFILE"] = "testing"
os.environ["FLASK_SECRET"] = "test-flask-secret-key"
os.environ["JWT_SECRET"] = "test-jwt-secret-key"
os.environ["DATABASE_URI"] = "sqlite:///:memory:"
os.environ["PROJECT_FOLDER"] = "/tmp/vanilla-webapp"
