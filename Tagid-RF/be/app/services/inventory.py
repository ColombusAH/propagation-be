"""Inventory Management Service.

Provides functions for:
- Taking inventory snapshots from readers
- Retrieving inventory history
- Calculating stock levels
"""

import logging
from datetime import datetime
from typing import List, Optional

from app.db.prisma import prisma_client

logger = logging.getLogger(__name__)


async def take_snapshot(reader_id: str, tags: List[dict]) -> Optional[str]:
    """
    Create an inventory snapshot for a reader.

    Args:
        reader_id: The ID of the RFID reader.
        tags: List of tag data dicts with 'epc', 'rssi', etc.

    Returns:
        The snapshot ID if successful, None otherwise.
    """
    try:
        async with prisma_client.client as db:
            # Create snapshot record
            snapshot = await db.inventorysnapshot.create(
                data={
                    "readerId": reader_id,
                    "itemCount": len(tags),
                    "timestamp": datetime.utcnow(),
                }
            )

            # Create snapshot items
            for tag_data in tags:
                epc = tag_data.get("epc")
                if not epc:
                    continue

                # Try to find existing RfidTag
                rfid_tag = await db.rfidtag.find_unique(where={"epc": epc})

                if rfid_tag:
                    await db.inventorysnapshotitem.create(
                        data={
                            "snapshotId": snapshot.id,
                            "tagId": rfid_tag.id,
                            "epc": epc,
                            "rssi": tag_data.get("rssi", 0),
                        }
                    )
                else:
                    # Tag not registered - log warning
                    logger.warning(f"Unknown tag scanned: {epc}")

            logger.info(f"Snapshot created: {snapshot.id} with {len(tags)} items")
            return snapshot.id

    except Exception as e:
        logger.error(f"Failed to create snapshot: {e}", exc_info=True)
        return None


async def get_latest_snapshot(reader_id: str) -> Optional[dict]:
    """
    Get the most recent inventory snapshot for a reader.
    """
    try:
        async with prisma_client.client as db:
            snapshot = await db.inventorysnapshot.find_first(
                where={"readerId": reader_id}, order={"timestamp": "desc"}, include={"items": True}
            )

            if snapshot:
                return {
                    "id": snapshot.id,
                    "readerId": snapshot.readerId,
                    "timestamp": snapshot.timestamp.isoformat(),
                    "itemCount": snapshot.itemCount,
                    "items": [{"epc": item.epc, "rssi": item.rssi} for item in snapshot.items],
                }
            return None

    except Exception as e:
        logger.error(f"Failed to get snapshot: {e}", exc_info=True)
        return None


async def get_inventory_history(reader_id: str, limit: int = 10) -> List[dict]:
    """
    Get inventory snapshot history for a reader.
    """
    try:
        async with prisma_client.client as db:
            snapshots = await db.inventorysnapshot.find_many(
                where={"readerId": reader_id},
                order={"timestamp": "desc"},
                take=limit,
            )

            return [
                {
                    "id": s.id,
                    "timestamp": s.timestamp.isoformat(),
                    "itemCount": s.itemCount,
                }
                for s in snapshots
            ]

    except Exception as e:
        logger.error(f"Failed to get history: {e}", exc_info=True)
        return []


async def get_current_stock(store_id: Optional[str] = None) -> dict:
    """
    Get current stock levels based on the latest snapshots from all readers.
    """
    try:
        async with prisma_client.client as db:
            # Get all readers (optionally filtered by store)
            where_clause = {"storeId": store_id} if store_id else {}
            readers = await db.rfidreader.find_many(where=where_clause)

            total_items = 0
            reader_summaries = []

            for reader in readers:
                latest = await get_latest_snapshot(reader.id)
                if latest:
                    total_items += latest["itemCount"]
                    reader_summaries.append(
                        {
                            "readerId": reader.id,
                            "readerName": reader.name,
                            "location": reader.location,
                            "itemCount": latest["itemCount"],
                            "lastScan": latest["timestamp"],
                        }
                    )

            return {
                "totalItems": total_items,
                "readerCount": len(readers),
                "readers": reader_summaries,
            }

    except Exception as e:
        logger.error(f"Failed to get stock: {e}", exc_info=True)
        return {"totalItems": 0, "readerCount": 0, "readers": []}
