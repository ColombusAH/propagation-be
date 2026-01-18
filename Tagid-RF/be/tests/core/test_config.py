"""
Tests for app/core/config.py - Settings loading and validation.
"""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.core import config  # Import the module to reload it if needed
from app.core.config import Settings, get_settings


def test_settings_defaults():
    """Test default values for settings."""
    # We need to provide required fields to instantiate Settings
    env_vars = {
        "DATABASE_URL": "postgresql://user:pass@localhost/db",
        "SECRET_KEY": "test_secret",
        "GOOGLE_CLIENT_ID": "google_id",
    }

    with patch.dict(os.environ, env_vars, clear=True):
        settings = Settings()

        # Check defaults
        assert settings.API_V1_STR == "/api/v1"
        assert settings.DEBUG is False
        assert settings.MODE == "development"
        assert settings.DEFAULT_CURRENCY == "ILS"
        assert settings.ENABLE_THEFT_DETECTION is True

        # Check required
        assert settings.DATABASE_URL == env_vars["DATABASE_URL"]
        assert settings.SECRET_KEY == env_vars["SECRET_KEY"]


def test_settings_override():
    """Test overriding defaults with environment variables."""
    env_vars = {
        "DATABASE_URL": "postgresql://prod:pass@db/prod",
        "SECRET_KEY": "prod_secret",
        "GOOGLE_CLIENT_ID": "google_id_prod",
        "DEBUG": "True",
        "PROJECT_NAME": "Production App",
        "RFID_READER_IP": "10.0.0.50",
    }

    with patch.dict(os.environ, env_vars, clear=True):
        settings = Settings()

        assert settings.DEBUG is True
        assert settings.PROJECT_NAME == "Production App"
        assert settings.RFID_READER_IP == "10.0.0.50"


def test_settings_missing_required():
    """Test that missing required fields raises ValidationError."""
    # Missing DATABASE_URL and others
    # Missing DATABASE_URL and others
    # Force missing required values to ensure validation fails
    try:
        # Passing None to required str fields triggers validation error
        Settings(DATABASE_URL=None, SECRET_KEY=None, _env_file=None)
        assert False, "Should have raised ValidationError"
    except ValidationError as e:
        errors = str(e)
        assert "DATABASE_URL" in errors or "database_url" in errors
        assert "SECRET_KEY" in errors or "secret_key" in errors


def test_get_settings_caching():
    """Test that get_settings uses lru_cache."""
    # First call
    s1 = get_settings()
    # Second call
    s2 = get_settings()

    assert s1 is s2
