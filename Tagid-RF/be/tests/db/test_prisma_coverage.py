"""
Comprehensive tests for PrismaClient and database functions.
Covers: PrismaClient, init_db, shutdown_db
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestPrismaClient:
    """Tests for PrismaClient singleton."""

    def test_prisma_client_singleton(self):
        """Test that PrismaClient returns singleton instance."""
        from app.db.prisma import PrismaClient
        
        client1 = PrismaClient()
        client2 = PrismaClient()
        
        assert client1 is client2

    def test_prisma_client_property(self):
        """Test client property creates Prisma instance."""
        from app.db.prisma import PrismaClient
        
        pc = PrismaClient()
        client = pc.client
        
        assert client is not None

    @pytest.mark.asyncio
    async def test_prisma_connect(self):
        """Test database connection."""
        with patch("app.db.prisma.Prisma") as MockPrisma:
            mock_client = MagicMock()
            mock_client.connect = AsyncMock()
            MockPrisma.return_value = mock_client
            
            from app.db.prisma import PrismaClient
            pc = PrismaClient()
            pc._client = mock_client
            
            await pc.connect()
            mock_client.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_prisma_disconnect(self):
        """Test database disconnection."""
        mock_client = MagicMock()
        mock_client.disconnect = AsyncMock()
        
        from app.db.prisma import PrismaClient
        pc = PrismaClient()
        pc._client = mock_client
        
        await pc.disconnect()
        mock_client.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_prisma_disconnect_when_not_connected(self):
        """Test disconnection when not connected."""
        from app.db.prisma import PrismaClient
        pc = PrismaClient()
        pc._client = None
        
        # Should not raise
        await pc.disconnect()


class TestInitDb:
    """Tests for init_db function."""

    @pytest.mark.asyncio
    async def test_init_db_success(self):
        """Test successful database initialization."""
        with patch("app.db.prisma.prisma_client") as mock_pc:
            mock_pc.connect = AsyncMock()
            mock_pc.client.user.find_first = AsyncMock(return_value=None)
            
            from app.db.prisma import init_db
            mock_app = MagicMock()
            
            await init_db(mock_app)
            
            mock_pc.connect.assert_called_once()
            assert hasattr(mock_app.state, 'prisma')

    @pytest.mark.asyncio
    async def test_init_db_table_not_found(self):
        """Test init_db when tables don't exist."""
        from prisma.errors import TableNotFoundError
        
        with patch("app.db.prisma.prisma_client") as mock_pc:
            mock_pc.connect = AsyncMock()
            mock_pc.disconnect = AsyncMock()
            mock_pc.client.user.find_first = AsyncMock(side_effect=TableNotFoundError("user"))
            
            from app.db.prisma import init_db
            mock_app = MagicMock()
            
            with pytest.raises(TableNotFoundError):
                await init_db(mock_app)


class TestShutdownDb:
    """Tests for shutdown_db function."""

    @pytest.mark.asyncio
    async def test_shutdown_db_success(self):
        """Test successful database shutdown."""
        with patch("app.db.prisma.prisma_client") as mock_pc:
            mock_pc.disconnect = AsyncMock()
            
            from app.db.prisma import shutdown_db
            mock_app = MagicMock()
            
            await shutdown_db(mock_app)
            
            mock_pc.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_shutdown_db_error(self):
        """Test shutdown_db handles errors."""
        with patch("app.db.prisma.prisma_client") as mock_pc:
            mock_pc.disconnect = AsyncMock(side_effect=Exception("Disconnect error"))
            
            from app.db.prisma import shutdown_db
            mock_app = MagicMock()
            
            with pytest.raises(Exception):
                await shutdown_db(mock_app)
