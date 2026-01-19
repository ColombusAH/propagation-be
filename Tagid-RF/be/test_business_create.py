import asyncio
import uuid

from prisma import Prisma


async def test_create():
    db = Prisma()
    await db.connect()
    try:
        slug = f"test-{uuid.uuid4().hex[:8]}"
        print(f"Attempting to create business with slug: {slug}")
        b = await db.business.create(data={"name": "Test Business", "slug": slug})
        print(f"SUCCESS: Created business with ID {b.id}")
    except Exception as e:
        print(f"FAILURE: {e}")
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(test_create())
