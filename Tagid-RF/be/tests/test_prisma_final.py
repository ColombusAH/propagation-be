import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from prisma.errors import PrismaError
from app.db.prisma import PrismaClient, prisma_client, init_db, shutdown_db

@pytest.mark.asyncio
async def test_init_db_error():
    """Test init_db when connection fails."""
    mock_app = MagicMock()
    
    with patch.object(prisma_client, 'connect', new_callable=AsyncMock) as mock_connect:
        mock_connect.side_effect = Exception("DB Error")
        
        with pytest.raises(Exception):
            await init_db(mock_app)

@pytest.mark.asyncio
async def test_shutdown_db_error():
    """Test shutdown_db when disconnect fails."""
    mock_app = MagicMock()
    
    with patch.object(prisma_client, 'disconnect', new_callable=AsyncMock) as mock_disconnect:
        mock_disconnect.side_effect = Exception("Disconnect Error")
        
        with pytest.raises(Exception):
            await shutdown_db(mock_app)

@pytest.mark.asyncio
async def test_prisma_get_db_context():
    """Test PrismaClient get_db context manager."""
    pc = PrismaClient()
    
    with patch.object(pc, 'connect', new_callable=AsyncMock), \
         patch.object(pc, 'disconnect', new_callable=AsyncMock):
        async with pc.get_db() as db:
            assert db is not None
