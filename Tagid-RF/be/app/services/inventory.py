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
                where={"readerId": reader_id},
                order={"timestamp": "desc"},
                include={"items": True},
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
    Returns aggregation by product.
    """
    try:
        async with prisma_client.client as db:
            # 1. Get all readers (optionally filtered by store)
            where_clause = {"storeId": store_id} if store_id else {}
            readers = await db.rfidreader.find_many(where=where_clause)

            total_items = 0
            reader_summaries = []
            epc_seen = set() # To avoid double counting if multiple readers see same tag (optional, but good practice)
            
            # This map will hold product_id -> count
            product_counts = {}

            # 2. Get latest snapshot from each reader
            for reader in readers:
                latest = await db.inventorysnapshot.find_first(
                    where={"readerId": reader.id},
                    order={"timestamp": "desc"},
                    include={"items": {"include": {"tag": {"include": {"product": True}}}}},
                )
                
                if latest:
                    # Count distinct items specific to this reader query logic
                    # ideally we reconcile overlapping readers, but for now simple sum
                    snapshot_count = latest.itemCount
                    total_items += snapshot_count
                    
                    reader_summaries.append(
                        {
                            "readerId": reader.id,
                            "readerName": reader.name,
                            "location": reader.location,
                            "itemCount": snapshot_count,
                            "lastScan": latest.timestamp.isoformat(),
                        }
                    )
                    
                    # Aggregate per product
                    for item in latest.items:
                        # item.tag is the RfidTag relation
                        if item.tag and item.tag.product:
                            p_id = item.tag.product.id
                            p_name = item.tag.product.name
                            p_sku = item.tag.product.sku
                            p_min = getattr(item.tag.product, "minStock", 0) # Use getattr for safety during migration
                            
                            if p_id not in product_counts:
                                product_counts[p_id] = {
                                    "id": p_id,
                                    "name": p_name,
                                    "sku": p_sku,
                                    "minStock": p_min,
                                    "count": 0,
                                    "status": "OK"
                                }
                            
                            # Simple logic: assume latest snapshot is truth. 
                            # If we want to handle overlaps, we need to track unique EPCs globally.
                            # taking simple approach:
                            product_counts[p_id]["count"] += 1

            # 3. Also include products with 0 stock (that exist in DB but weren't scanned)
            all_products = await db.product.find_many()
            for p in all_products:
                if p.id not in product_counts:
                     product_counts[p.id] = {
                        "id": p.id,
                        "name": p.name,
                        "sku": p.sku,
                        "minStock": getattr(p, "minStock", 0),
                        "count": 0,
                        "status": "LOW_STOCK" if getattr(p, "minStock", 0) > 0 else "OK"
                    }
            
            # Calculate status
            products_list = list(product_counts.values())
            for p in products_list:
                if p["count"] < p["minStock"]:
                    p["status"] = "LOW_STOCK"
                elif p["count"] == 0 and p["minStock"] > 0:
                     p["status"] = "OUT_OF_STOCK"
            
            return {
                "totalItems": total_items,
                "readerCount": len(readers),
                "readers": reader_summaries,
                "products": products_list
            }

    except Exception as e:
        logger.error(f"Failed to get stock: {e}", exc_info=True)
        return {"totalItems": 0, "readerCount": 0, "readers": [], "products": []}
