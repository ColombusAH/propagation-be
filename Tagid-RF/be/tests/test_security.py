import pytest
from jose import jwt

from app.core.config import get_settings
from app.core.security import create_access_token, get_password_hash, verify_password

settings = get_settings()


def test_password_hashing():
    password = "testpass"
    hashed = get_password_hash(password)
    print(f"DEBUG: password={password}, len={len(password)}")
    print(f"DEBUG: hashed={hashed}, len={len(hashed)}")
    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_create_access_token():
    data = {"sub": "test@example.com", "user_id": 1}
    token = create_access_token(data)
    assert isinstance(token, str)

    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert payload["sub"] == "test@example.com"
    assert payload["user_id"] == 1
    assert "exp" in payload
