
import asyncio
from prisma import Prisma

async def main():
    db = Prisma()
    try:
        await db.connect()
        user_email = 'eliran8hadad@gmail.com'
        user = await db.user.find_unique(where={'email': user_email})
        
        if user:
            print(f"Deleting data for user {user.id}...")
            # Delete related data first
            await db.alertrecipient.delete_many(where={'userId': user.id})
            await db.notification.delete_many(where={'userId': user.id})
            await db.notificationpreference.delete_many(where={'userId': user.id})
            await db.availabilitypreference.delete_many(where={'userId': user.id})
            
            # Finally delete user
            deleted = await db.user.delete(where={'id': user.id})
            print(f"Successfully deleted user: {deleted.email}")
        else:
            print("User not found.")
            
        await db.disconnect()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
