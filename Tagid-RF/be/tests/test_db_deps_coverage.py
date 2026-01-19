from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest
from app.db.dependencies import get_db
from fastapi import HTTPException, Request, status


@pytest.mark.asyncio
async def test_get_db_wrapper_missing():
    """Test get_db raises 503 if prisma wrapper is missing from state."""
    mock_request = MagicMock(spec=Request)
    mock_request.app.state.prisma = None

    with pytest.raises(HTTPException) as exc:
        await get_db(mock_request)
    assert exc.value.status_code == 503
    assert "not configured correctly" in exc.value.detail


@pytest.mark.asyncio
async def test_get_db_client_missing():
    """Test get_db raises 503 if prisma wrapper has no client."""
    mock_request = MagicMock(spec=Request)
    # Mocking app.state.prisma to have no client
    mock_wrapper = MagicMock()
    del mock_wrapper.client
    mock_request.app.state.prisma = object()

    with pytest.raises(HTTPException) as exc:
        await get_db(mock_request)
    assert exc.value.status_code == 503
    assert "not configured correctly" in exc.value.detail


@pytest.mark.asyncio
async def test_get_db_reconnect_failure():
    """Test get_db raises 503 if reconnection fails."""
    mock_request = MagicMock(spec=Request)
    mock_client = MagicMock()
    mock_client.is_connected.return_value = False
    mock_client.connect = AsyncMock(side_effect=Exception("Connection failed"))

    mock_wrapper = MagicMock()
    mock_wrapper.client = mock_client
    mock_request.app.state.prisma = mock_wrapper

    with pytest.raises(HTTPException) as exc:
        await get_db(mock_request)
    assert exc.value.status_code == 503
    assert "Could not connect" in exc.value.detail


@pytest.mark.asyncio
async def test_get_db_attribute_error():
    """Test get_db raises 503 on AttributeError (e.g. state missing)."""
    mock_request = MagicMock(spec=Request)
    del mock_request.app.state  # Simulate missing state

    with pytest.raises(HTTPException) as exc:
        await get_db(mock_request)
    assert exc.value.status_code == 503
    assert "initialization error" in exc.value.detail


@pytest.mark.asyncio
async def test_get_db_unexpected_error():
    """Test get_db raises 500 on unexpected error."""
    mock_request = MagicMock(spec=Request)
    # Mocking app.state access to raise Exception using PropertyMock
    mock_app = MagicMock()
    p = PropertyMock(side_effect=Exception("Unexpected"))
    type(mock_app).state = p
    mock_request.app = mock_app

    with pytest.raises(HTTPException) as exc:
        await get_db(mock_request)
    assert exc.value.status_code == 500
    assert "internal error" in exc.value.detail
