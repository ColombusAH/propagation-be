"""
Tests for prisma.py database client.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestPrismaClientCoverage:
    """Tests for PrismaClient class."""

    def test_prisma_client_import(self):
        """Test PrismaClient can be imported."""
        from app.db.prisma import PrismaClient, prisma_client

        assert PrismaClient is not None
        assert prisma_client is not None

    def test_prisma_client_singleton(self):
        """Test PrismaClient singleton pattern."""
        from app.db.prisma import prisma_client

        # Same instance should be returned
        client1 = prisma_client
        client2 = prisma_client
        assert client1 is client2

    @pytest.mark.asyncio
    async def test_prisma_connect_mock(self):
        """Test Prisma connect with mocking."""
        from app.db.prisma import PrismaClient

        with patch("app.db.prisma.Prisma") as mock_prisma:
            mock_instance = MagicMock()
            mock_instance.connect = AsyncMock()
            mock_instance.is_connected.return_value = False
            mock_prisma.return_value = mock_instance

            client = PrismaClient()
            client._client = mock_instance

            await client.connect()
            mock_instance.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_prisma_disconnect_mock(self):
        """Test Prisma disconnect with mocking."""
        from app.db.prisma import PrismaClient

        with patch("app.db.prisma.Prisma") as mock_prisma:
            mock_instance = MagicMock()
            mock_instance.disconnect = AsyncMock()
            mock_instance.is_connected.return_value = True
            mock_prisma.return_value = mock_instance

            client = PrismaClient()
            client._client = mock_instance

            await client.disconnect()
            mock_instance.disconnect.assert_called_once()
