import asyncio
from app.db.prisma import prisma_client
from prisma.models import PushSubscription

async def check():
    try:
        await prisma_client.connect()
        count = await PushSubscription.prisma().count()
        print(f"SUBSCRIPTION_COUNT: {count}")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        await prisma_client.disconnect()

if __name__ == "__main__":
    asyncio.run(check())
