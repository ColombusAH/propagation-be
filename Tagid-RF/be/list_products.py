import asyncio
from app.db.prisma import prisma_client

async def list_products():
    await prisma_client.connect()
    products = await prisma_client.client.product.find_many()
    for p in products:
        print(f"ID: {p.id}, Name: {p.name}, Price: {p.price}")
    await prisma_client.disconnect()

if __name__ == "__main__":
    asyncio.run(list_products())
