"""
Unit tests for core security with mocking.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.unit
class TestCoreSecurity:
    """Tests for core security module."""

    def test_get_password_hash_unique(self):
        """Test password hash is unique each time due to salt."""
        from app.core.security import get_password_hash
        
        password = "test_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Should be different due to salt
        assert hash1 != hash2

    def test_verify_password_handles_unicode(self):
        """Test password verification handles unicode."""
        from app.core.security import get_password_hash, verify_password
        
        password = "פסוורד_מורכב_123!@#"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("wrong", hashed) is False

    def test_create_access_token_contains_sub(self):
        """Test access token contains subject."""
        from app.core.security import create_access_token, verify_access_token
        
        token = create_access_token(data={"sub": "user_id_123"})
        payload = verify_access_token(token)
        
        assert payload["sub"] == "user_id_123"

    def test_create_access_token_with_extra_data(self):
        """Test access token with extra data."""
        from app.core.security import create_access_token, verify_access_token
        
        token = create_access_token(data={"sub": "user123", "role": "ADMIN"})
        payload = verify_access_token(token)
        
        assert payload["sub"] == "user123"
        assert payload["role"] == "ADMIN"


@pytest.mark.unit
class TestCoreConfig:
    """Tests for core config module."""

    def test_settings_import(self):
        """Test Settings can be imported."""
        from app.core.config import Settings
        
        assert Settings is not None

    def test_get_settings_import(self):
        """Test get_settings can be imported."""
        from app.core.config import get_settings
        
        assert get_settings is not None
        assert callable(get_settings)

    def test_get_settings_returns_instance(self):
        """Test get_settings returns Settings instance."""
        from app.core.config import get_settings, Settings
        
        settings = get_settings()
        
        assert isinstance(settings, Settings)

    def test_settings_has_database_url(self):
        """Test Settings has database URL attribute."""
        from app.core.config import get_settings
        
        settings = get_settings()
        
        assert hasattr(settings, 'DATABASE_URL') or hasattr(settings, 'database_url')

    def test_settings_has_secret_key(self):
        """Test Settings has secret key attribute."""
        from app.core.config import get_settings
        
        settings = get_settings()
        
        assert hasattr(settings, 'SECRET_KEY') or hasattr(settings, 'secret_key')
