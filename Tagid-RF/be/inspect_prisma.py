import asyncio
from app.db.prisma import prisma_client


async def main():
    try:
        await prisma_client.connect()
        print("Connected to Prisma.")
        print("Available attributes on prisma_client.client:")
        for attr in dir(prisma_client.client):
            if not attr.startswith("_"):  # Skip private attributes
                print(f" - {attr}")

        await prisma_client.disconnect()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
