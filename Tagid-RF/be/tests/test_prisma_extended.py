import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.db.prisma import init_db, shutdown_db

@pytest.mark.asyncio
async def test_init_db_success():
    """Test init_db connects prisma."""
    mock_app = MagicMock()
    with patch("app.db.prisma.prisma_client") as mock_client:
        mock_client.connect = AsyncMock()
        await init_db(mock_app)
        mock_client.connect.assert_called_once()

@pytest.mark.asyncio
async def test_shutdown_db_success():
    """Test shutdown_db disconnects prisma."""
    mock_app = MagicMock()
    with patch("app.db.prisma.prisma_client") as mock_client:
        mock_client.disconnect = AsyncMock()
        await shutdown_db(mock_app)
        mock_client.disconnect.assert_called_once()
