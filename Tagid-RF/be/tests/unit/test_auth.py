"""
Unit tests for authentication and security functions.
"""

import pytest

from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_access_token,
    verify_password,
)


@pytest.mark.unit
def test_password_hashing():
    """Test password hashing and verification."""
    password = "testpassword123"
    hashed = get_password_hash(password)

    # Verify correct password
    assert verify_password(password, hashed)

    # Verify incorrect password
    assert not verify_password("wrongpassword", hashed)

    # Verify different hashes for same password
    hashed2 = get_password_hash(password)
    assert hashed != hashed2  # Should be different due to salt


@pytest.mark.unit
def test_create_access_token():
    """Test JWT token creation."""
    user_id = "test-user-123"
    token = create_access_token(data={"sub": user_id})

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.unit
def test_decode_access_token():
    """Test JWT token decoding."""
    user_id = "test-user-123"
    token = create_access_token(data={"sub": user_id})

    payload = verify_access_token(token)
    assert payload is not None
    assert payload["sub"] == user_id


@pytest.mark.unit
def test_decode_invalid_token():
    """Test decoding invalid JWT token."""
    invalid_token = "invalid.token.here"

    payload = verify_access_token(invalid_token)
    assert payload is None
