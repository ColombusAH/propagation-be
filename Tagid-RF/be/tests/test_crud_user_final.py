from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.crud.user import (
    authenticate_user,
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user_google_info,
)


@pytest.mark.asyncio
async def test_get_user_by_email_not_found():
    mock_db = MagicMock()
    mock_db.user.find_unique = AsyncMock(return_value=None)

    result = await get_user_by_email(mock_db, "notfound@example.com")
    assert result is None


@pytest.mark.asyncio
async def test_update_user_google_info_not_found():
    mock_db = MagicMock()
    # Use generic Exception to avoid RecordNotFoundError constructor issues
    mock_db.user.update = AsyncMock(side_effect=Exception("User not found"))

    with pytest.raises(Exception, match="User not found"):
        await update_user_google_info(mock_db, "nonexistent", "google-sub")


@pytest.mark.asyncio
async def test_update_user_google_info_error():
    mock_db = MagicMock()
    mock_db.user.update = AsyncMock(side_effect=Exception("DB Error"))

    with pytest.raises(Exception, match="DB Error"):
        await update_user_google_info(mock_db, "user-123", "google-sub")


@pytest.mark.asyncio
async def test_create_user_success():
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_user.id = "user-123"
    mock_db.user.create = AsyncMock(return_value=mock_user)

    with patch("app.core.security.get_password_hash", return_value="hashed_pass"):
        result = await create_user(
            db=mock_db,
            email="new@example.com",
            password="pass",
            name="Name",
            phone="123",
            address="Addr",
            business_id="B1",
            role="CUSTOMER",
        )
        assert result == mock_user
        mock_db.user.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_user_error():
    mock_db = MagicMock()
    mock_db.user.create = AsyncMock(side_effect=Exception("Creation Fail"))

    with patch("app.core.security.get_password_hash", return_value="hashed_pass"):
        with pytest.raises(Exception, match="Creation Fail"):
            await create_user(mock_db, "e", "p", "n", "ph", "a", "b")


@pytest.mark.asyncio
async def test_authenticate_user_success():
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_user.password = "hashed_pass"

    with patch("app.crud.user.get_user_by_email", return_value=mock_user):
        with patch("app.core.security.verify_password", return_value=True):
            result = await authenticate_user(mock_db, "test@example.com", "password")
            assert result == mock_user


@pytest.mark.asyncio
async def test_authenticate_user_not_found():
    mock_db = MagicMock()
    with patch("app.crud.user.get_user_by_email", return_value=None):
        result = await authenticate_user(mock_db, "notfound@example.com", "password")
        assert result is None


@pytest.mark.asyncio
async def test_authenticate_user_no_password():
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_user.password = None  # OAuth only user

    with patch("app.crud.user.get_user_by_email", return_value=mock_user):
        result = await authenticate_user(mock_db, "oauth@example.com", "password")
        assert result is None


@pytest.mark.asyncio
async def test_authenticate_user_invalid_password():
    mock_db = MagicMock()
    mock_user = MagicMock()
    mock_user.password = "hashed_pass"

    with patch("app.crud.user.get_user_by_email", return_value=mock_user):
        with patch("app.core.security.verify_password", return_value=False):
            result = await authenticate_user(mock_db, "test@example.com", "wrong")
            assert result is None


@pytest.mark.asyncio
async def test_authenticate_user_error():
    mock_db = MagicMock()
    with patch("app.crud.user.get_user_by_email", side_effect=Exception("Auth Error")):
        with pytest.raises(Exception, match="Auth Error"):
            await authenticate_user(mock_db, "e", "p")
