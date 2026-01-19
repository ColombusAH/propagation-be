from unittest.mock import AsyncMock, MagicMock

import pytest
from app.crud.user import get_user_by_email, get_user_by_id, update_user_google_info


@pytest.mark.asyncio
async def test_get_user_by_id_found():
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_db.user.find_unique = AsyncMock(return_value=mock_user)

    result = await get_user_by_id(mock_db, 1)
    assert result == mock_user


@pytest.mark.asyncio
async def test_get_user_by_email_found():
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_db.user.find_unique = AsyncMock(return_value=mock_user)

    result = await get_user_by_email(mock_db, "test@example.com")
    assert result == mock_user


@pytest.mark.asyncio
async def test_get_user_by_email_error():
    mock_db = MagicMock()
    mock_db.user.find_unique = AsyncMock(side_effect=Exception("DB Error"))
    with pytest.raises(Exception):
        await get_user_by_email(mock_db, "error@example.com")


@pytest.mark.asyncio
async def test_get_user_by_id_error():
    mock_db = MagicMock()
    mock_db.user.find_unique = AsyncMock(side_effect=Exception("DB Error"))
    with pytest.raises(Exception):
        await get_user_by_id(mock_db, "error-id")
