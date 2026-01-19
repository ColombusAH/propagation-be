"""
End-to-End Flow Simulation Script

This script simulates a complete business flow:
1. Create a Business (Network)
2. Create a Store within that Business
3. Create a Store Manager
4. Register Products with RFID Tags
5. Create a Customer
6. Simulate Shopping & Checkout
7. Verify Security (Gate scan)
"""

import asyncio
import logging
import sys
import os

# Add the current directory to sys.path to allow imports from app
sys.path.append(os.getcwd())

from app.db.prisma import prisma_client
from app.services.inventory import take_snapshot
from app.services.theft_detection import TheftDetectionService
from app.services.tag_encryption import get_encryption_service

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def run_simulation():
    await prisma_client.connect()
    try:
        logger.info("🚀 Starting End-to-End Simulation...")

        # 1. Create a Business (Network)
        business_name = f"Test Network {os.urandom(2).hex()}"
        business = await prisma_client.client.business.create(
            data={
                "name": business_name,
                "slug": f"network-{os.urandom(2).hex()}"
            }
        )
        logger.info(f"✅ Created Network: {business.name} (ID: {business.id})")

        # 2. Create a Store
        store = await prisma_client.client.store.create(
            data={
                "name": "Main Downtown Store",
                "businessId": business.id,
                "slug": f"store-{os.urandom(2).hex()}"
            }
        )
        logger.info(f"✅ Created Store: {store.name} (Slug: {store.slug})")

        # 3. Create a Store Manager
        manager_email = f"manager_{os.urandom(2).hex()}@example.com"
        manager = await prisma_client.client.user.create(
            data={
                "email": manager_email,
                "name": "John Manager",
                "phone": "050-1234567",
                "address": "Store St. 1",
                "role": "STORE_MANAGER",
                "businessId": business.id,
                "receiveTheftAlerts": True
            }
        )
        logger.info(f"✅ Created Store Manager: {manager.name} ({manager.email})")

        # 4. Create RFID Reader (Gate)
        reader = await prisma_client.client.rfidreader.create(
            data={
                "name": "Main Exit Gate",
                "ipAddress": f"192.168.1.{os.urandom(1)[0]}",
                "type": "GATE",
                "storeId": store.id
            }
        )
        logger.info(f"✅ Registered Reader: {reader.name} at {reader.ipAddress}")

        # 5. Register Products with RFID Tags
        tags_to_create = [
            {"epc": f"E280{os.urandom(4).hex().upper()}", "desc": "Premium Nike Sneakers", "price": 45000},
            {"epc": f"E280{os.urandom(4).hex().upper()}", "desc": "Adidas Running Shirt", "price": 12000}
        ]
        
        created_tags = []
        for t in tags_to_create:
            tag = await prisma_client.client.rfidtag.create(
                data={
                    "epc": t["epc"],
                    "productDescription": t["desc"],
                    "productId": f"SKU-{os.urandom(2).hex().upper()}",
                    "isPaid": False,
                    "status": "ACTIVE"
                }
            )
            created_tags.append(tag)
            logger.info(f"📦 Tagged Product: {t['desc']} (EPC: {t['epc']})")

        # 6. Simulate Inventory Snapshot
        logger.info("📸 Taking initial inventory snapshot...")
        snapshot_id = await take_snapshot(reader.id, [{"epc": t.epc, "rssi": -45} for t in created_tags])
        logger.info(f"✅ Inventory Snapshot Created: {snapshot_id}")

        # 7. Simulate Security Violation (Unpaid item at Gate)
        logger.info("🚨 Simulating security scan (Unpaid item)...")
        theft_service = TheftDetectionService()
        is_paid = await theft_service.check_tag_payment_status(created_tags[0].epc, location=reader.name)
        if not is_paid:
            logger.warning(f"❌ Security Alert Triggered for {created_tags[0].productDescription}!")

        # 8. Simulate Customer Checkout
        logger.info("💳 Simulating Customer Checkout...")
        for tag in created_tags:
            await prisma_client.client.rfidtag.update(
                where={"id": tag.id},
                data={"isPaid": True, "paidAt": asyncio.get_event_loop().time()} # Simplified for mock
            )
        logger.info("✅ Payment processed for all items.")

        # 9. Verify Security (Paid item at Gate)
        logger.info("🛡️ Simulating security scan (Paid item)...")
        is_paid_after = await theft_service.check_tag_payment_status(created_tags[0].epc, location=reader.name)
        if is_paid_after:
            logger.info(f"✅ Security Clearance: {created_tags[0].productDescription} is verified as PAID.")

        logger.info("\n🏆 Simulation Finished Successfully!")
        logger.info(f"Network Slug: {business.slug}")
        logger.info(f"Store Slug: {store.slug}")

    except Exception as e:
        logger.error(f"❌ Simulation Failed: {e}", exc_info=True)
    finally:
        await prisma_client.disconnect()

if __name__ == "__main__":
    asyncio.run(run_simulation())
