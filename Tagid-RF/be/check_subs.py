import asyncio
from app.services.database import SessionLocal
from prisma import Prisma

async def main():
    prisma = Prisma()
    await prisma.connect()
    count = await prisma.pushsubscription.count()
    print(f"Subscription count: {count}")
    await prisma.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
