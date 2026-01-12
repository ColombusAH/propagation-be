import pytest
from app.db.dependencies import get_db
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import Request

@pytest.mark.asyncio
async def test_get_db_dependency():
    """Test get_db dependency with mock Request."""
    mock_request = MagicMock(spec=Request)
    mock_app = MagicMock()
    mock_prisma_wrapper = MagicMock()
    mock_prisma_client = MagicMock()
    
    mock_prisma_client.is_connected.return_value = True
    mock_prisma_wrapper.client = mock_prisma_client
    mock_app.state.prisma = mock_prisma_wrapper
    mock_request.app = mock_app
    
    db = await get_db(mock_request)
    assert db == mock_prisma_client

@pytest.mark.asyncio
async def test_get_db_dependency_not_connected():
    """Test get_db dependency when not connected."""
    mock_request = MagicMock(spec=Request)
    mock_app = MagicMock()
    mock_prisma_wrapper = MagicMock()
    mock_prisma_client = MagicMock()
    
    mock_prisma_client.is_connected.return_value = False
    mock_prisma_client.connect = AsyncMock()
    mock_prisma_wrapper.client = mock_prisma_client
    mock_app.state.prisma = mock_prisma_wrapper
    mock_request.app = mock_app
    
    db = await get_db(mock_request)
    assert db == mock_prisma_client
    mock_prisma_client.connect.assert_called_once()
