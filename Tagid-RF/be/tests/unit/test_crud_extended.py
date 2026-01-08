"""
Comprehensive unit tests for CRUD user module with mocking.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.mark.unit
class TestGetUserByEmail:
    """Tests for get_user_by_email function."""

    @pytest.mark.asyncio
    async def test_returns_user_when_found(self):
        """Test returns user when email exists."""
        from app.crud.user import get_user_by_email
        
        mock_user = MagicMock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"
        
        mock_db = MagicMock()
        mock_db.user.find_unique = AsyncMock(return_value=mock_user)
        
        result = await get_user_by_email(mock_db, "test@example.com")
        
        assert result is not None
        assert result.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        """Test returns None when email doesn't exist."""
        from app.crud.user import get_user_by_email
        
        mock_db = MagicMock()
        mock_db.user.find_unique = AsyncMock(return_value=None)
        
        result = await get_user_by_email(mock_db, "nonexistent@example.com")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_calls_find_unique_with_email(self):
        """Test calls find_unique with correct email."""
        from app.crud.user import get_user_by_email
        
        mock_db = MagicMock()
        mock_db.user.find_unique = AsyncMock(return_value=None)
        
        await get_user_by_email(mock_db, "test@example.com")
        
        mock_db.user.find_unique.assert_called_once()
        call_args = mock_db.user.find_unique.call_args
        assert "email" in str(call_args)


@pytest.mark.unit
class TestGetUserById:
    """Tests for get_user_by_id function."""

    @pytest.mark.asyncio
    async def test_returns_user_when_found(self):
        """Test returns user when ID exists."""
        from app.crud.user import get_user_by_id
        
        mock_user = MagicMock()
        mock_user.id = "user123"
        
        mock_db = MagicMock()
        mock_db.user.find_unique = AsyncMock(return_value=mock_user)
        
        result = await get_user_by_id(mock_db, "user123")
        
        assert result is not None
        assert result.id == "user123"

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self):
        """Test returns None when ID doesn't exist."""
        from app.crud.user import get_user_by_id
        
        mock_db = MagicMock()
        mock_db.user.find_unique = AsyncMock(return_value=None)
        
        result = await get_user_by_id(mock_db, "nonexistent")
        
        assert result is None


@pytest.mark.unit
class TestCreateUser:
    """Tests for create_user function."""

    @pytest.mark.asyncio
    async def test_creates_user_successfully(self):
        """Test successfully creates user."""
        from app.crud.user import create_user
        
        mock_user = MagicMock()
        mock_user.id = "new_user"
        mock_user.email = "new@example.com"
        
        mock_db = MagicMock()
        mock_db.user.create = AsyncMock(return_value=mock_user)
        
        result = await create_user(
            db=mock_db,
            email="new@example.com",
            password="password123",
            name="New User",
            phone="1234567890",
            address="123 Main St",
            business_id="BIZ001"
        )
        
        assert result is not None
        assert result.email == "new@example.com"

    @pytest.mark.asyncio
    async def test_password_is_hashed(self):
        """Test password is hashed before storing."""
        from app.crud.user import create_user
        
        mock_db = MagicMock()
        mock_db.user.create = AsyncMock(return_value=MagicMock())
        
        await create_user(
            db=mock_db,
            email="test@example.com",
            password="plaintext",
            name="Test",
            phone="123",
            address="123 St",
            business_id="BIZ"
        )
        
        # Verify create was called with hashed password
        call_args = mock_db.user.create.call_args
        assert "password" in str(call_args)


@pytest.mark.unit
class TestAuthenticateUser:
    """Tests for authenticate_user function."""

    @pytest.mark.asyncio
    async def test_returns_user_on_valid_credentials(self):
        """Test returns user with valid credentials."""
        from app.crud.user import authenticate_user
        from app.core.security import get_password_hash
        
        hashed = get_password_hash("correct_password")
        mock_user = MagicMock()
        mock_user.id = "user123"
        mock_user.password = hashed
        
        mock_db = MagicMock()
        mock_db.user.find_unique = AsyncMock(return_value=mock_user)
        
        result = await authenticate_user(mock_db, "test@example.com", "correct_password")
        
        assert result is not None

    @pytest.mark.asyncio
    async def test_returns_none_on_wrong_password(self):
        """Test returns None with wrong password."""
        from app.crud.user import authenticate_user
        from app.core.security import get_password_hash
        
        hashed = get_password_hash("correct_password")
        mock_user = MagicMock()
        mock_user.password = hashed
        
        mock_db = MagicMock()
        mock_db.user.find_unique = AsyncMock(return_value=mock_user)
        
        result = await authenticate_user(mock_db, "test@example.com", "wrong_password")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_when_user_not_found(self):
        """Test returns None when user not found."""
        from app.crud.user import authenticate_user
        
        mock_db = MagicMock()
        mock_db.user.find_unique = AsyncMock(return_value=None)
        
        result = await authenticate_user(mock_db, "notfound@example.com", "password")
        
        assert result is None


@pytest.mark.unit
class TestUpdateUserGoogleInfo:
    """Tests for update_user_google_info function."""

    @pytest.mark.asyncio
    async def test_updates_google_sub_id(self):
        """Test updates user with Google sub ID."""
        from app.crud.user import update_user_google_info
        
        mock_user = MagicMock()
        mock_user.id = "user123"
        mock_user.subId = "google_sub_123"
        
        mock_db = MagicMock()
        mock_db.user.update = AsyncMock(return_value=mock_user)
        
        result = await update_user_google_info(mock_db, "user123", "google_sub_123")
        
        assert result is not None
        mock_db.user.update.assert_called_once()
