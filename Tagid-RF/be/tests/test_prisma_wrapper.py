from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.db.prisma import PrismaClient, init_db, prisma_client, shutdown_db


@pytest.mark.asyncio
async def test_prisma_client_singleton():
    """Test PrismaClient is a singleton."""
    client1 = PrismaClient()
    client2 = PrismaClient()
    assert client1 is client2


def test_prisma_client_property():
    """Test client property creates Prisma instance."""
    pc = PrismaClient()
    client = pc.client
    assert client is not None


@pytest.mark.asyncio
async def test_init_db_success():
    """Test init_db connects and sets app state."""
    mock_app = MagicMock()
    with patch.object(prisma_client, "connect", new_callable=AsyncMock):
        await init_db(mock_app)
        assert mock_app.state.prisma is prisma_client


@pytest.mark.asyncio
async def test_shutdown_db_success():
    """Test shutdown_db disconnects."""
    mock_app = MagicMock()
    with patch.object(
        prisma_client, "disconnect", new_callable=AsyncMock
    ) as mock_disconnect:
        await shutdown_db(mock_app)
        mock_disconnect.assert_called_once()
