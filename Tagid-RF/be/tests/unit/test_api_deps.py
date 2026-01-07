"""
Unit tests for API dependencies and permissions.
Using actual imports from the codebase.
"""

import pytest


@pytest.mark.unit
class TestAuthDependencies:
    """Tests for authentication dependencies."""

    def test_get_current_user_import(self):
        """Test get_current_user dependency can be imported."""
        from app.api.dependencies.auth import get_current_user
        
        assert callable(get_current_user)


@pytest.mark.unit
class TestCoreDeps:
    """Tests for core dependencies."""

    def test_core_deps_import(self):
        """Test core deps module can be imported."""
        from app.core import deps
        
        assert deps is not None


@pytest.mark.unit
class TestPermissionsModule:
    """Tests for permission system."""

    def test_permissions_module_import(self):
        """Test permissions module can be imported."""
        from app.core import permissions
        
        assert permissions is not None


@pytest.mark.unit
class TestSecurityFunctions:
    """Tests for security functions."""

    def test_get_password_hash(self):
        """Test password hashing."""
        from app.core.security import get_password_hash
        
        hashed = get_password_hash("testpassword")
        
        assert hashed is not None
        assert hashed != "testpassword"
        assert len(hashed) > 20

    def test_verify_password_correct(self):
        """Test correct password verification."""
        from app.core.security import get_password_hash, verify_password
        
        password = "securepassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test incorrect password verification."""
        from app.core.security import get_password_hash, verify_password
        
        hashed = get_password_hash("correctpassword")
        
        assert verify_password("wrongpassword", hashed) is False

    def test_create_access_token(self):
        """Test JWT token creation."""
        from app.core.security import create_access_token
        
        token = create_access_token(data={"sub": "user123"})
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50

    def test_verify_access_token_valid(self):
        """Test valid JWT token verification."""
        from app.core.security import create_access_token, verify_access_token
        
        token = create_access_token(data={"sub": "user123"})
        payload = verify_access_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user123"

    def test_verify_access_token_invalid(self):
        """Test invalid JWT token verification."""
        from app.core.security import verify_access_token
        
        payload = verify_access_token("invalid.token.here")
        
        assert payload is None

    def test_token_includes_expiration(self):
        """Test JWT token includes expiration."""
        from app.core.security import create_access_token, verify_access_token
        
        token = create_access_token(data={"sub": "user123"})
        payload = verify_access_token(token)
        
        assert "exp" in payload


@pytest.mark.unit
class TestPasswordSecurity:
    """Tests for password security features."""

    def test_different_hashes_same_password(self):
        """Test same password produces different hashes (salt)."""
        from app.core.security import get_password_hash
        
        password = "testpassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2

    def test_special_characters_password(self):
        """Test password with special characters."""
        from app.core.security import get_password_hash, verify_password
        
        password = "P@$$w0rd!#$%^&*()"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_unicode_password(self):
        """Test password with unicode characters."""
        from app.core.security import get_password_hash, verify_password
        
        password = "סיסמה_בעברית_123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
