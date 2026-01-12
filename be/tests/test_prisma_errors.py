import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from prisma.errors import PrismaError
from app.db.prisma import PrismaClient

@pytest.mark.asyncio
async def test_prisma_connect_error():
    """Test PrismaClient connect error handling."""
    # Create a fresh instance for this test
    pc = PrismaClient.__new__(PrismaClient)
    pc._client = MagicMock()
    pc._client.connect = AsyncMock(side_effect=PrismaError("Connection failed"))
    
    with pytest.raises(PrismaError):
        await pc.connect()

@pytest.mark.asyncio
async def test_prisma_disconnect_when_no_client():
    """Test PrismaClient disconnect when no client exists."""
    pc = PrismaClient.__new__(PrismaClient)
    pc._client = None
    # Should not raise, just return
    await pc.disconnect()
