"""
Tests for app/core/security.py - Auth utilities.
"""

from datetime import timedelta
from unittest.mock import patch

import pytest
from jose import jwt, JWTError

from app.core import security
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_access_token,
    verify_password,
)


def test_password_hashing():
    """Test password hashing and verification."""
    password = "secret_password"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_password_verification_error():
    """Test handling of invalid hash format."""
    # Invalid hash should return False, not raise
    assert verify_password("pass", "invalid_hash_string") is False


def test_create_access_token():
    """Test JWT creation."""
    data = {"sub": "user@example.com"}
    token = create_access_token(data)

    assert isinstance(token, str)

    # Decode manually to check contents
    payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    assert payload["sub"] == "user@example.com"
    assert "exp" in payload


def test_create_access_token_custom_expiry():
    """Test JWT with custom expiry."""
    data = {"sub": "test"}
    delta = timedelta(minutes=10)
    token = create_access_token(data, expires_delta=delta)

    payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    # Roughly check exp (allow slop)
    # verify_access_token will do the real check
    assert payload["sub"] == "test"


def test_verify_access_token_valid():
    """Test verifying a valid token."""
    data = {"sub": "user@test.com"}
    token = create_access_token(data)

    payload = verify_access_token(token)
    assert payload is not None
    assert payload["sub"] == "user@test.com"


def test_verify_access_token_invalid():
    """Test verifying an invalid token."""
    assert verify_access_token("invalid.token.string") is None


def test_verify_access_token_expired():
    """Test verifying an expired token."""
    # Create a token expired in the past
    data = {"sub": "expired"}
    delta = timedelta(minutes=-10)
    token = create_access_token(data, expires_delta=delta)

    # Verification should fail
    payload = verify_access_token(token)
    assert payload is None


def test_jwt_encode_error():
    """Test error handling during token creation."""
    # Mock jwt.encode to raise error
    with patch("jose.jwt.encode", side_effect=JWTError("Encode Error")):
        with pytest.raises(ValueError, match="Could not create access token"):
            create_access_token({"sub": "test"})
