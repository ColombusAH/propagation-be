from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.api.dependencies.auth import get_current_user


@pytest.mark.asyncio
async def test_get_current_user_found():
    """Test get_current_user when user exists in DB."""
    mock_token = MagicMock()
    mock_db = MagicMock()
    mock_user = MagicMock()

    # Patch get_user_by_id which is what is used in the module
    with (
        patch("app.api.dependencies.auth.verify_access_token", return_value={"user_id": 1}),
        patch("app.api.dependencies.auth.get_user_by_id", new_callable=AsyncMock) as mock_get,
    ):

        mock_get.return_value = mock_user
        result = await get_current_user(mock_token, mock_db)
        assert result == mock_user


@pytest.mark.asyncio
async def test_get_current_user_not_found():
    """Test get_current_user when user missing in DB."""
    mock_token = MagicMock()
    mock_db = MagicMock()

    with (
        patch(
            "app.api.dependencies.auth.verify_access_token",
            return_value={"user_id": 999},
        ),
        patch("app.api.dependencies.auth.get_user_by_id", new_callable=AsyncMock) as mock_get,
    ):

        mock_get.return_value = None
        with pytest.raises(HTTPException) as exc:
            await get_current_user(mock_token, mock_db)
        assert exc.value.status_code == 401
