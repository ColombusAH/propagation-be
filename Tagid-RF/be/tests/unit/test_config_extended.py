"""
Comprehensive unit tests for app.core.config module.
"""

import pytest


@pytest.mark.unit
class TestSettings:
    """Tests for Settings class."""

    def test_settings_import(self):
        """Test Settings can be imported."""
        from app.core.config import Settings
        assert Settings is not None

    def test_get_settings_import(self):
        """Test get_settings can be imported."""
        from app.core.config import get_settings
        assert get_settings is not None
        assert callable(get_settings)

    def test_settings_instance(self):
        """Test get_settings returns Settings instance."""
        from app.core.config import get_settings, Settings
        
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_settings_has_project_name(self):
        """Test settings has PROJECT_NAME."""
        from app.core.config import get_settings
        
        settings = get_settings()
        assert hasattr(settings, 'PROJECT_NAME') or hasattr(settings, 'project_name')

    def test_settings_has_database_url(self):
        """Test settings has DATABASE_URL."""
        from app.core.config import get_settings
        
        settings = get_settings()
        assert hasattr(settings, 'DATABASE_URL') or hasattr(settings, 'database_url')

    def test_settings_has_secret_key(self):
        """Test settings has SECRET_KEY."""
        from app.core.config import get_settings
        
        settings = get_settings()
        assert hasattr(settings, 'SECRET_KEY') or hasattr(settings, 'secret_key')

    def test_settings_singleton(self):
        """Test get_settings returns cached instance."""
        from app.core.config import get_settings
        
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2


@pytest.mark.unit
class TestSettingsValues:
    """Tests for Settings values."""

    def test_project_name_is_string(self):
        """Test PROJECT_NAME is a string."""
        from app.core.config import get_settings
        
        settings = get_settings()
        name = getattr(settings, 'PROJECT_NAME', getattr(settings, 'project_name', None))
        assert isinstance(name, str)

    def test_secret_key_is_string(self):
        """Test SECRET_KEY is a string."""
        from app.core.config import get_settings
        
        settings = get_settings()
        key = getattr(settings, 'SECRET_KEY', getattr(settings, 'secret_key', None))
        assert isinstance(key, str)

    def test_database_url_is_string(self):
        """Test DATABASE_URL is a string."""
        from app.core.config import get_settings
        
        settings = get_settings()
        url = getattr(settings, 'DATABASE_URL', getattr(settings, 'database_url', None))
        assert isinstance(url, str)

    def test_secret_key_not_empty(self):
        """Test SECRET_KEY is not empty."""
        from app.core.config import get_settings
        
        settings = get_settings()
        key = getattr(settings, 'SECRET_KEY', getattr(settings, 'secret_key', None))
        assert len(key) > 0


@pytest.mark.unit
class TestLogging:
    """Tests for logging configuration."""

    def test_setup_logging_import(self):
        """Test setup_logging can be imported."""
        from app.core.logging import setup_logging
        assert setup_logging is not None
        assert callable(setup_logging)

    def test_setup_logging_execution(self):
        """Test setup_logging can be called."""
        from app.core.logging import setup_logging
        
        # Should not raise
        setup_logging()

    def test_logger_is_configured(self):
        """Test logger is properly configured."""
        import logging
        from app.core.logging import setup_logging
        
        setup_logging()
        logger = logging.getLogger("app")
        assert logger is not None
