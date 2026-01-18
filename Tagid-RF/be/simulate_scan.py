import asyncio
import logging
import sys
import os

# Set up path to import app modules
sys.path.append(os.getcwd())

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def simulate():
    """Simulate a tag scan event."""
    # Build connection
    from app.db.prisma import prisma_client

    try:
        await prisma_client.connect()
        logger.info("DB Connected.")

        from app.services.rfid_reader import rfid_reader_service
        from app.routers.websocket import manager

        # Test tag data
        fake_tag = {
            "epc": "E2806810000000001234FAKE",
            "rssi": -55.0,
            "antenna_port": 1,
            "pc": 3000,
            "timestamp": "2024-01-01T12:00:00Z",
        }

        logger.info(f"Simulating scan for tag: {fake_tag['epc']}")

        # Manually trigger process_tag
        await rfid_reader_service._process_tag(fake_tag)

        logger.info("Simulation complete. Check frontend for live update.")

    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await prisma_client.disconnect()


if __name__ == "__main__":
    asyncio.run(simulate())
