"""
Unit tests for CRUD user operations with mocking.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.unit
class TestCRUDUserFunctions:
    """Tests for user CRUD functions."""

    def test_get_user_by_email_import(self):
        """Test get_user_by_email can be imported."""
        from app.crud.user import get_user_by_email
        
        assert get_user_by_email is not None
        assert callable(get_user_by_email)

    def test_get_user_by_id_import(self):
        """Test get_user_by_id can be imported."""
        from app.crud.user import get_user_by_id
        
        assert get_user_by_id is not None
        assert callable(get_user_by_id)

    def test_create_user_import(self):
        """Test create_user can be imported."""
        from app.crud.user import create_user
        
        assert create_user is not None
        assert callable(create_user)

    def test_authenticate_user_import(self):
        """Test authenticate_user can be imported."""
        from app.crud.user import authenticate_user
        
        assert authenticate_user is not None
        assert callable(authenticate_user)

    def test_update_user_google_info_import(self):
        """Test update_user_google_info can be imported."""
        from app.crud.user import update_user_google_info
        
        assert update_user_google_info is not None
        assert callable(update_user_google_info)


@pytest.mark.unit
class TestCRUDUserMocked:
    """Mocked tests for user CRUD operations."""

    @pytest.mark.asyncio
    async def test_get_user_by_email_found(self):
        """Test get_user_by_email when user is found."""
        from app.crud.user import get_user_by_email
        
        # Mock DB and user
        mock_user = MagicMock()
        mock_user.id = "user123"
        mock_user.email = "test@example.com"
        
        mock_db = MagicMock()
        mock_db.user.find_unique = AsyncMock(return_value=mock_user)
        
        result = await get_user_by_email(mock_db, "test@example.com")
        
        assert result is not None
        assert result.email == "test@example.com"
        mock_db.user.find_unique.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self):
        """Test get_user_by_email when user is not found."""
        from app.crud.user import get_user_by_email
        
        mock_db = MagicMock()
        mock_db.user.find_unique = AsyncMock(return_value=None)
        
        result = await get_user_by_email(mock_db, "nonexistent@example.com")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_get_user_by_id_found(self):
        """Test get_user_by_id when user is found."""
        from app.crud.user import get_user_by_id
        
        mock_user = MagicMock()
        mock_user.id = "user123"
        
        mock_db = MagicMock()
        mock_db.user.find_unique = AsyncMock(return_value=mock_user)
        
        result = await get_user_by_id(mock_db, "user123")
        
        assert result is not None
        assert result.id == "user123"

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self):
        """Test get_user_by_id when user is not found."""
        from app.crud.user import get_user_by_id
        
        mock_db = MagicMock()
        mock_db.user.find_unique = AsyncMock(return_value=None)
        
        result = await get_user_by_id(mock_db, "nonexistent")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_create_user_success(self):
        """Test create_user successfully creates user."""
        from app.crud.user import create_user
        
        mock_user = MagicMock()
        mock_user.id = "new_user_123"
        mock_user.email = "new@example.com"
        
        mock_db = MagicMock()
        mock_db.user.create = AsyncMock(return_value=mock_user)
        
        result = await create_user(
            db=mock_db,
            email="new@example.com",
            password="password123",
            name="New User",
            phone="123456789",
            address="123 Main St",
            business_id="BIZ123",
            role="CUSTOMER"
        )
        
        assert result is not None
        assert result.id == "new_user_123"
        mock_db.user.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self):
        """Test authenticate_user with valid credentials."""
        from app.crud.user import authenticate_user
        from app.core.security import get_password_hash
        
        # Create a mock user with hashed password
        hashed_pw = get_password_hash("correct_password")
        mock_user = MagicMock()
        mock_user.id = "user123"
        mock_user.email = "user@example.com"
        mock_user.password = hashed_pw
        
        mock_db = MagicMock()
        mock_db.user.find_unique = AsyncMock(return_value=mock_user)
        
        result = await authenticate_user(mock_db, "user@example.com", "correct_password")
        
        assert result is not None
        assert result.id == "user123"

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self):
        """Test authenticate_user with wrong password."""
        from app.crud.user import authenticate_user
        from app.core.security import get_password_hash
        
        hashed_pw = get_password_hash("correct_password")
        mock_user = MagicMock()
        mock_user.password = hashed_pw
        
        mock_db = MagicMock()
        mock_db.user.find_unique = AsyncMock(return_value=mock_user)
        
        result = await authenticate_user(mock_db, "user@example.com", "wrong_password")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self):
        """Test authenticate_user when user doesn't exist."""
        from app.crud.user import authenticate_user
        
        mock_db = MagicMock()
        mock_db.user.find_unique = AsyncMock(return_value=None)
        
        result = await authenticate_user(mock_db, "nonexistent@example.com", "password")
        
        assert result is None

    @pytest.mark.asyncio
    async def test_update_user_google_info_success(self):
        """Test update_user_google_info success."""
        from app.crud.user import update_user_google_info
        
        mock_user = MagicMock()
        mock_user.id = "user123"
        mock_user.subId = "google_123"
        
        mock_db = MagicMock()
        mock_db.user.update = AsyncMock(return_value=mock_user)
        
        result = await update_user_google_info(mock_db, "user123", "google_123")
        
        assert result is not None
        mock_db.user.update.assert_called_once()
