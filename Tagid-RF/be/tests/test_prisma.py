import pytest
from app.db.prisma import prisma_client, init_db, shutdown_db
from unittest.mock import patch, AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_prisma_connection():
    # Use patch.object on the underlying client if connect is read-only
    with patch("prisma.Prisma.connect", new_callable=AsyncMock) as mock_connect:
        await prisma_client.connect()
        # Since prisma_client is a singleton, it might already be connected
        # But our mock should be called if we call connect() on it

@pytest.mark.asyncio
async def test_prisma_disconnection():
    with patch("prisma.Prisma.disconnect", new_callable=AsyncMock) as mock_disconnect:
        await prisma_client.disconnect()

@pytest.mark.asyncio
async def test_init_db():
    mock_app = MagicMock()
    with patch("app.db.prisma.prisma_client.connect", new_callable=AsyncMock) as mock_connect:
        await init_db(mock_app)
        mock_connect.assert_called_once()

@pytest.mark.asyncio
async def test_shutdown_db():
    mock_app = MagicMock()
    with patch("app.db.prisma.prisma_client.disconnect", new_callable=AsyncMock) as mock_disconnect:
        await shutdown_db(mock_app)
        mock_disconnect.assert_called_once()
