import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.crud.user import get_user_by_id, get_user_by_email, update_user_google_info

@pytest.mark.asyncio
async def test_get_user_by_id_found():
    """Test get_user_by_id when user exists."""
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_db.user.find_unique = AsyncMock(return_value=mock_user)
    
    result = await get_user_by_id(mock_db, "user-123")
    assert result == mock_user

@pytest.mark.asyncio
async def test_get_user_by_id_not_found():
    """Test get_user_by_id when user doesn't exist."""
    mock_db = MagicMock()
    mock_db.user.find_unique = AsyncMock(return_value=None)
    
    result = await get_user_by_id(mock_db, "nonexistent")
    assert result is None

@pytest.mark.asyncio
async def test_get_user_by_email_found():
    """Test get_user_by_email when user exists."""
    mock_db = MagicMock()
    mock_user = MagicMock()
    # get_user_by_email uses find_unique, not find_first
    mock_db.user.find_unique = AsyncMock(return_value=mock_user)
    
    result = await get_user_by_email(mock_db, "test@example.com")
    assert result == mock_user

@pytest.mark.asyncio
async def test_update_user_google_info_success():
    """Test update_user_google_info."""
    mock_db = MagicMock()
    mock_db.user.update = AsyncMock(return_value=MagicMock())
    
    result = await update_user_google_info(mock_db, "user-123", "google-sub-id")
    mock_db.user.update.assert_called_once()
