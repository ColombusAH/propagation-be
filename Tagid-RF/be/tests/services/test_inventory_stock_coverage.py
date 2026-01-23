"""
Targeted tests for inventory.get_current_stock coverage.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.inventory import get_current_stock
from tests.mock_utils import MockModel


@pytest.mark.asyncio
async def test_get_current_stock_full_flow():
    """
    Test get_current_stock with actual loop execution.
    We mock prisma_client to return readers and snapshots.
    """
    with patch("app.services.inventory.prisma_client") as mock_prisma:
        mock_db = MagicMock()
        mock_ctx = MagicMock()
        mock_ctx.__aenter__ = AsyncMock(return_value=mock_db)
        mock_ctx.__aexit__ = AsyncMock(return_value=None)
        mock_prisma.client = mock_ctx

        # Readers setup
        readers = [
            MockModel(id="reader1", name="R1", location="Loc1"),
            MockModel(id="reader2", name="R2", location="Loc2"),
        ]
        mock_db.rfidreader.find_many = AsyncMock(return_value=readers)

        # Snapshots setup for get_latest_snapshot
        # Note: inventory.py calls get_latest_snapshot which does its own DB query.
        # Since we use the SAME mock_db context, we need to handle the calls.

        # We can mock get_latest_snapshot using patch to simplify logic and ensure isolation?
        # NO, we want to cover the loop lines in get_current_stock explicitly.
        # But wait, lines 133-150 contain the loop AND the call to get_latest_snapshot.
        # If we mock get_latest_snapshot, we still exercise the loop.

        with patch("app.services.inventory.get_latest_snapshot") as mock_get_latest:
            mock_get_latest.side_effect = [
                {"itemCount": 10, "timestamp": "2023-01-01"},  # reader1
                {"itemCount": 5, "timestamp": "2023-01-01"},  # reader2
            ]

            result = await get_current_stock()

            assert result["totalItems"] == 15
            assert result["readerCount"] == 2
            assert len(result["readers"]) == 2
            assert result["readers"][0]["readerId"] == "reader1"
