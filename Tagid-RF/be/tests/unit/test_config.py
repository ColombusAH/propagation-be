"""
Unit tests for core configuration and settings.
"""

import pytest
import os


@pytest.mark.unit
class TestSettings:
    """Tests for app settings configuration."""

    def test_settings_accessible(self):
        """Test settings can be accessed."""
        from app.core.config import get_settings
        
        settings = get_settings()
        
        assert settings is not None

    def test_settings_has_project_name(self):
        """Test settings has project name."""
        from app.core.config import get_settings
        
        settings = get_settings()
        
        assert hasattr(settings, 'PROJECT_NAME')
        assert settings.PROJECT_NAME is not None

    def test_settings_has_api_prefix(self):
        """Test settings has API prefix."""
        from app.core.config import get_settings
        
        settings = get_settings()
        
        assert hasattr(settings, 'API_V1_STR')
        assert settings.API_V1_STR.startswith('/api')

    def test_settings_has_cors_origins(self):
        """Test settings has CORS origins list."""
        from app.core.config import get_settings
        
        settings = get_settings()
        
        assert hasattr(settings, 'BACKEND_CORS_ORIGINS')
        assert isinstance(settings.BACKEND_CORS_ORIGINS, (list, str))


@pytest.mark.unit
class TestSecurityConfig:
    """Tests for security configuration."""

    def test_password_hash_import(self):
        """Test password hash functions can be imported."""
        from app.core.security import get_password_hash, verify_password
        
        assert callable(get_password_hash)
        assert callable(verify_password)

    def test_token_functions_import(self):
        """Test token functions can be imported."""
        from app.core.security import create_access_token, verify_access_token
        
        assert callable(create_access_token)
        assert callable(verify_access_token)


@pytest.mark.unit
class TestLoggingConfig:
    """Tests for logging configuration."""

    def test_setup_logging_callable(self):
        """Test setup_logging function exists."""
        from app.core.logging import setup_logging
        
        assert callable(setup_logging)

    def test_setup_logging_runs(self):
        """Test setup_logging can be called."""
        from app.core.logging import setup_logging
        
        # Should not raise
        setup_logging()


@pytest.mark.unit
class TestDatabaseConfig:
    """Tests for database configuration."""

    def test_prisma_client_import(self):
        """Test prisma client can be imported."""
        from app.db.prisma import prisma_client
        
        assert prisma_client is not None

    def test_sqlalchemy_base_import(self):
        """Test SQLAlchemy Base can be imported."""
        from app.services.database import Base
        
        assert Base is not None

    def test_get_db_function(self):
        """Test get_db function exists."""
        from app.services.database import get_db
        
        assert callable(get_db)

    def test_init_db_function(self):
        """Test init_db function exists."""
        from app.services.database import init_db
        
        assert callable(init_db)
