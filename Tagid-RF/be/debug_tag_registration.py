import asyncio
import logging

from prisma import Prisma

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_db():
    logger.info("Initializing Prisma...")
    db = Prisma()
    try:
        await db.connect()
        logger.info("Connected to DB.")

        logger.info("Querying unregistered tags...")
        tags = await db.rfidtag.find_many(where={"status": "UNREGISTERED"}, take=5)
        logger.info(f"Found {len(tags)} unregistered tags.")
        for tag in tags:
            logger.info(f"Tag: {tag.id}, EPC: {tag.epc}, Status: {tag.status}")

    except Exception as e:
        logger.error(f"Error during DB operation: {e}", exc_info=True)
    finally:
        if db.is_connected():
            await db.disconnect()
            logger.info("Disconnected.")


if __name__ == "__main__":
    asyncio.run(test_db())
