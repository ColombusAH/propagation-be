"""
Comprehensive tests for core dependencies (deps.py).
Covers: get_db, get_current_user
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException


class TestGetDb:
    """Tests for get_db dependency."""

    @pytest.mark.asyncio
    async def test_get_db_yields_connection(self):
        """Test that get_db yields a database connection."""
        with patch("app.core.deps.prisma_client") as mock_client:
            mock_db = MagicMock()
            mock_client.get_db.return_value.__aenter__ = AsyncMock(return_value=mock_db)
            mock_client.get_db.return_value.__aexit__ = AsyncMock()

            from app.core.deps import get_db
            
            async for db in get_db():
                assert db is not None


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self):
        """Test getting user with valid token."""
        with patch("app.core.deps.jwt") as mock_jwt, \
             patch("app.core.deps.settings") as mock_settings:
            
            mock_settings.SECRET_KEY = "test_secret"
            mock_jwt.decode.return_value = {"sub": "user-123"}
            
            mock_db = MagicMock()
            mock_user = MagicMock(id="user-123", email="test@example.com")
            mock_db.user.find_unique = AsyncMock(return_value=mock_user)

            from app.core.deps import get_current_user
            
            user = await get_current_user(db=mock_db, token="valid_token")
            assert user is not None

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test handling invalid JWT token."""
        from jose import JWTError
        
        with patch("app.core.deps.jwt") as mock_jwt, \
             patch("app.core.deps.settings") as mock_settings:
            
            mock_settings.SECRET_KEY = "test_secret"
            mock_jwt.decode.side_effect = JWTError("Invalid token")
            
            mock_db = MagicMock()

            from app.core.deps import get_current_user
            
            with pytest.raises(HTTPException) as exc:
                await get_current_user(db=mock_db, token="invalid_token")
            
            assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_no_user_id(self):
        """Test handling token without user ID."""
        with patch("app.core.deps.jwt") as mock_jwt, \
             patch("app.core.deps.settings") as mock_settings:
            
            mock_settings.SECRET_KEY = "test_secret"
            mock_jwt.decode.return_value = {"sub": None}  # No user ID
            
            mock_db = MagicMock()

            from app.core.deps import get_current_user
            
            with pytest.raises(HTTPException) as exc:
                await get_current_user(db=mock_db, token="token_without_sub")
            
            assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_not_found(self):
        """Test handling user not found in database."""
        with patch("app.core.deps.jwt") as mock_jwt, \
             patch("app.core.deps.settings") as mock_settings:
            
            mock_settings.SECRET_KEY = "test_secret"
            mock_jwt.decode.return_value = {"sub": "user-123"}
            
            mock_db = MagicMock()
            mock_db.user.find_unique = AsyncMock(return_value=None)  # User not found

            from app.core.deps import get_current_user
            
            with pytest.raises(HTTPException) as exc:
                await get_current_user(db=mock_db, token="valid_token")
            
            assert exc.value.status_code == 401
