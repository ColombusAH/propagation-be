
import asyncio
from prisma import Prisma

async def check_business():
    db = Prisma()
    await db.connect()
    
    try:
        businesses = await db.business.find_many()
        print(f"Found {len(businesses)} businesses")
        for b in businesses:
            print(f"ID: {b.id}, Name: {b.name}, Slug: {getattr(b, 'slug', 'MISSING_ATTR')}")
            
    except Exception as e:
        print(f"Error checking business: {e}")
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(check_business())
