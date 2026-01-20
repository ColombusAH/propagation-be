from unittest.mock import MagicMock, patch

import pytest
from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.security import create_access_token, verify_access_token

settings = get_settings()


def test_create_access_token_error():
    """Test error handling during token creation."""
    with patch("jose.jwt.encode", side_effect=JWTError("Encoding failed")):
        with pytest.raises(ValueError) as exc:
            create_access_token({"sub": "test"})
        assert "Could not create access token" in str(exc.value)


def test_verify_access_token_failure():
    """Test verification failure with invalid token."""
    assert verify_access_token("invalid.token.here") is None


def test_verify_access_token_exception():
    """Test verification with patched exception."""
    with patch("jose.jwt.decode", side_effect=Exception("Unexpected")):
        assert verify_access_token("some.token") is None


def test_verify_access_token_expired():
    """Test verification of expired token."""
    import datetime
    from datetime import timedelta, timezone

    data = {
        "sub": "test",
        "exp": datetime.datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    assert verify_access_token(token) is None
