"""
Mock-based tests for Inventory Service.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.inventory import (
    get_current_stock,
    get_inventory_history,
    get_latest_snapshot,
    take_snapshot,
)
from tests.mock_utils import MockModel


class TestInventoryServiceMock:

    @patch("app.services.inventory.prisma_client")
    async def test_take_snapshot_success(self, mock_prisma_wrapper):
        """Test creating an inventory snapshot."""
        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_db)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_prisma_wrapper.client = mock_client_instance

        # Mock DB creation
        snapshot = MockModel(id="snap1")
        mock_db.inventorysnapshot.create = AsyncMock(return_value=snapshot)

        # Mock tag lookup
        rfid_tag = MockModel(id="t1", epc="E1")
        mock_db.rfidtag.find_unique = AsyncMock(return_value=rfid_tag)
        mock_db.inventorysnapshotitem.create = AsyncMock()

        tags = [{"epc": "E1", "rssi": -50}, {"epc": "E2", "rssi": -60}]

        # E2 not found
        async def mock_find_unique(where):
            if where["epc"] == "E1":
                return rfid_tag
            return None

        mock_db.rfidtag.find_unique.side_effect = mock_find_unique

        result = await take_snapshot("r1", tags)

        assert result == "snap1"
        mock_db.inventorysnapshot.create.assert_awaited_once()
        assert mock_db.inventorysnapshotitem.create.await_count == 1  # Only E1

    @patch("app.services.inventory.prisma_client")
    async def test_get_latest_snapshot(self, mock_prisma_wrapper):
        """Test retrieving latest snapshot."""
        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_db)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_prisma_wrapper.client = mock_client_instance

        item = MockModel(epc="E1", rssi=-50)
        snapshot = MockModel(
            id="snap1", readerId="r1", timestamp=datetime(2023, 1, 1), itemCount=1, items=[item]
        )
        mock_db.inventorysnapshot.find_first = AsyncMock(return_value=snapshot)

        result = await get_latest_snapshot("r1")

        assert result["id"] == "snap1"
        assert result["itemCount"] == 1
        assert result["items"][0]["epc"] == "E1"

    @patch("app.services.inventory.prisma_client")
    async def test_get_inventory_history(self, mock_prisma_wrapper):
        """Test retrieving inventory history."""
        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_db)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_prisma_wrapper.client = mock_client_instance

        snapshot = MockModel(id="snap1", timestamp=datetime(2023, 1, 1), itemCount=5)
        mock_db.inventorysnapshot.find_many = AsyncMock(return_value=[snapshot])

        result = await get_inventory_history("r1")

        assert len(result) == 1
        assert result[0]["id"] == "snap1"

    @patch("app.services.inventory.prisma_client")
    async def test_take_snapshot_error(self, mock_prisma_wrapper):
        """Test take_snapshot handles DB errors."""
        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_db)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_prisma_wrapper.client = mock_client_instance

        mock_db.inventorysnapshot.create = AsyncMock(side_effect=Exception("DB Error"))

        result = await take_snapshot("r1", [])
        assert result is None

    @patch("app.services.inventory.prisma_client")
    async def test_get_latest_snapshot_error(self, mock_prisma_wrapper):
        """Test get_latest_snapshot handles DB errors."""
        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_db)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_prisma_wrapper.client = mock_client_instance

        mock_db.inventorysnapshot.find_first = AsyncMock(side_effect=Exception("DB Error"))

        result = await get_latest_snapshot("r1")
        assert result is None

    @patch("app.services.inventory.prisma_client")
    async def test_get_inventory_history_error(self, mock_prisma_wrapper):
        """Test get_inventory_history handles DB errors."""
        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_db)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_prisma_wrapper.client = mock_client_instance

        mock_db.inventorysnapshot.find_many = AsyncMock(side_effect=Exception("DB Error"))

        result = await get_inventory_history("r1")
        assert result == []

    @patch("app.services.inventory.prisma_client")
    async def test_get_current_stock_error(self, mock_prisma_wrapper):
        """Test get_current_stock handles DB errors."""
        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_db)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_prisma_wrapper.client = mock_client_instance

        mock_db.rfidreader.find_many = AsyncMock(side_effect=Exception("DB Error"))

        result = await get_current_stock()
        assert result["totalItems"] == 0
        assert result["readerCount"] == 0

    @patch("app.services.inventory.prisma_client")
    async def test_take_snapshot_missing_epc(self, mock_prisma_wrapper):
        """Test take_snapshot skips items without EPC."""
        mock_db = MagicMock()
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_db)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_prisma_wrapper.client = mock_client_instance

        snapshot = MockModel(id="snap1")
        mock_db.inventorysnapshot.create = AsyncMock(return_value=snapshot)
        mock_db.rfidtag.find_unique = AsyncMock(return_value=None)

        # tag with no epc
        tags = [{"rssi": -50}]

        result = await take_snapshot("r1", tags)
        assert result == "snap1"
        # snapshot item create called 0 times because no valid epc
        mock_db.inventorysnapshotitem.create.assert_not_called()
