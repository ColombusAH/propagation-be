
import asyncio
from prisma import Prisma

async def main():
    db = Prisma()
    try:
        await db.connect()
        print("Connected to DB successfully.")
        
        users = await db.user.find_many()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f" - {user.email} (Verified: {user.isVerified})")
            
        businesses = await db.business.find_many()
        print(f"Found {len(businesses)} businesses:")
        for bus in businesses:
            print(f" - {bus.name} ({bus.id})")
            
        await db.disconnect()
    except Exception as e:
        print(f"Error connecting to DB: {e}")

if __name__ == "__main__":
    asyncio.run(main())
