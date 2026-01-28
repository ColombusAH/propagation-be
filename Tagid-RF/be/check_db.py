
import asyncio
from prisma import Prisma

async def main():
    db = Prisma()
    await db.connect()
    
    product_count = await db.product.count()
    print(f"Product count: {product_count}")
    
    if product_count > 0:
        products = await db.product.find_many(take=5)
        for p in products:
            print(f"Product: {p.name}, SKU: {p.sku}, Price: {p.price}")
    else:
        print("No products in database.")
        
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
