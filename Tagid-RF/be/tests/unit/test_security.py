"""
Comprehensive unit tests for app.core.security module.
"""

import pytest
from datetime import timedelta


@pytest.mark.unit
class TestPasswordHashing:
    """Tests for password hashing functions."""

    def test_get_password_hash_import(self):
        """Test get_password_hash can be imported."""
        from app.core.security import get_password_hash
        assert get_password_hash is not None
        assert callable(get_password_hash)

    def test_verify_password_import(self):
        """Test verify_password can be imported."""
        from app.core.security import verify_password
        assert verify_password is not None
        assert callable(verify_password)

    def test_hash_creates_string(self):
        """Test password hash returns string."""
        from app.core.security import get_password_hash
        
        hashed = get_password_hash("mypassword")
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_is_different_from_password(self):
        """Test hash is different from original password."""
        from app.core.security import get_password_hash
        
        password = "mypassword123"
        hashed = get_password_hash(password)
        assert hashed != password

    def test_same_password_different_hashes(self):
        """Test same password produces different hashes (salt)."""
        from app.core.security import get_password_hash
        
        password = "testpassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2

    def test_verify_correct_password(self):
        """Test verify_password returns True for correct password."""
        from app.core.security import get_password_hash, verify_password
        
        password = "correctpassword"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        """Test verify_password returns False for wrong password."""
        from app.core.security import get_password_hash, verify_password
        
        hashed = get_password_hash("correctpassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_verify_empty_password(self):
        """Test verify with empty password."""
        from app.core.security import get_password_hash, verify_password
        
        hashed = get_password_hash("somepassword")
        assert verify_password("", hashed) is False

    def test_hash_special_characters(self):
        """Test hashing password with special characters."""
        from app.core.security import get_password_hash, verify_password
        
        password = "P@ssw0rd!#$%^&*()"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_hash_unicode_password(self):
        """Test hashing password with unicode characters."""
        from app.core.security import get_password_hash, verify_password
        
        password = "סיסמה_בעברית_123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True



@pytest.mark.unit
class TestJWTTokens:
    """Tests for JWT token functions."""

    def test_create_access_token_import(self):
        """Test create_access_token can be imported."""
        from app.core.security import create_access_token
        assert create_access_token is not None
        assert callable(create_access_token)

    def test_verify_access_token_import(self):
        """Test verify_access_token can be imported."""
        from app.core.security import verify_access_token
        assert verify_access_token is not None
        assert callable(verify_access_token)

    def test_create_token_returns_string(self):
        """Test create_access_token returns string."""
        from app.core.security import create_access_token
        
        token = create_access_token(data={"sub": "user123"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_subject(self):
        """Test token contains subject after verification."""
        from app.core.security import create_access_token, verify_access_token
        
        token = create_access_token(data={"sub": "user123"})
        payload = verify_access_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"

    def test_token_with_extra_data(self):
        """Test token with extra data."""
        from app.core.security import create_access_token, verify_access_token
        
        token = create_access_token(data={"sub": "user123", "role": "ADMIN", "name": "Test"})
        payload = verify_access_token(token)
        assert payload["role"] == "ADMIN"
        assert payload["name"] == "Test"

    def test_token_has_expiration(self):
        """Test token has expiration claim."""
        from app.core.security import create_access_token, verify_access_token
        
        token = create_access_token(data={"sub": "user123"})
        payload = verify_access_token(token)
        assert "exp" in payload

    def test_token_different_subjects(self):
        """Test different tokens for different subjects."""
        from app.core.security import create_access_token
        
        token1 = create_access_token(data={"sub": "user1"})
        token2 = create_access_token(data={"sub": "user2"})
        assert token1 != token2
