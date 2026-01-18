"""
Tests for core configuration settings.
Covers: Settings, get_settings
"""

import pytest
from unittest.mock import patch


class TestSettings:
    """Tests for Settings configuration."""

    def test_settings_instance(self):
        """Test that settings instance is created."""
        from app.core.config import settings
        
        assert settings is not None
        assert settings.API_V1_STR == "/api/v1"
        assert settings.PROJECT_NAME == "Shifty"

    def test_settings_defaults(self):
        """Test default values."""
        from app.core.config import settings
        
        assert settings.DEFAULT_CURRENCY == "ILS"
        assert settings.JWT_ALGORITHM == "HS256"
        assert settings.SECURITY_HEADERS is True

    def test_settings_rfid_defaults(self):
        """Test RFID default settings."""
        from app.core.config import settings
        
        assert settings.RFID_READER_PORT == 4001
        assert settings.RFID_CONNECTION_TYPE == "tcp"
        assert settings.RFID_READER_ID == "M-200"

    def test_settings_cors_origins(self):
        """Test CORS origins configuration."""
        from app.core.config import settings
        
        assert "http://localhost:3000" in settings.BACKEND_CORS_ORIGINS
        assert "http://localhost:5173" in settings.BACKEND_CORS_ORIGINS


class TestGetSettings:
    """Tests for get_settings function."""

    def test_get_settings_returns_settings(self):
        """Test get_settings returns Settings instance."""
        from app.core.config import get_settings
        
        settings = get_settings()
        assert settings is not None
        assert hasattr(settings, 'API_V1_STR')

    def test_get_settings_cached(self):
        """Test get_settings uses lru_cache."""
        from app.core.config import get_settings
        
        settings1 = get_settings()
        settings2 = get_settings()
        
        # Should return the same cached instance
        assert settings1 is settings2
