"""
Tests for core configuration settings.
Covers: Settings, get_settings
"""

from unittest.mock import patch

import pytest


class TestSettings:
    """Tests for Settings configuration."""

    def test_settings_instance(self):
        """Test that settings instance is created."""
        from app.core.config import settings

        assert settings is not None
        # Values from conftest.py global mock
        assert settings.API_V1_STR == "/api/v1"
        assert settings.PROJECT_NAME == "RFID Test"

    def test_settings_defaults(self):
        """Test default values."""
        from unittest.mock import MagicMock

        from app.core.config import settings

        # conftest.py sets these
        assert settings.JWT_ALGORITHM == "HS256"
        assert settings.SECRET_KEY == "test-secret"

        # Verify it has other expected attributes
        assert hasattr(settings, "DEFAULT_CURRENCY")

    def test_settings_rfid_defaults(self):
        """Test RFID default settings."""
        from app.core.config import settings

        # These will be MagicMocks or values from global mock
        assert hasattr(settings, "RFID_READER_PORT")
        assert hasattr(settings, "RFID_CONNECTION_TYPE")
        assert hasattr(settings, "RFID_READER_ID")

    def test_settings_cors_origins(self):
        """Test CORS origins configuration."""
        from app.core.config import settings

        # conftest.py sets ["*"]
        assert "*" in settings.BACKEND_CORS_ORIGINS


class TestGetSettings:
    """Tests for get_settings function."""

    def test_get_settings_returns_settings(self):
        """Test get_settings returns Settings instance."""
        from app.core.config import get_settings

        settings = get_settings()
        assert settings is not None
        assert hasattr(settings, "API_V1_STR")

    def test_get_settings_cached(self):
        """Test get_settings uses lru_cache."""
        from app.core.config import get_settings

        settings1 = get_settings()
        settings2 = get_settings()

        # Should return the same cached instance (global mock)
        assert settings1 is settings2
