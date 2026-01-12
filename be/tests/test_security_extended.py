import pytest
from unittest.mock import patch, MagicMock
from app.core.security import verify_access_token, get_password_hash, verify_password, create_access_token

def test_verify_access_token_valid():
    """Test verify_access_token with valid token."""
    token = create_access_token(data={"sub": "test@example.com", "user_id": "123"})
    payload = verify_access_token(token)
    assert payload is not None
    assert payload["sub"] == "test@example.com"

def test_verify_access_token_invalid():
    """Test verify_access_token with invalid token."""
    payload = verify_access_token("invalid.token.here")
    assert payload is None

def test_verify_access_token_malformed():
    """Test verify_access_token with completely malformed token."""
    payload = verify_access_token("notavalidtoken")
    assert payload is None

def test_password_hashing_and_verification():
    """Test password hashing roundtrip."""
    password = "mysecurepassword"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)
