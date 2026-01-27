
import asyncio
import os
from prisma import Prisma

async def main():
    db = Prisma()
    try:
        # Manually set the DB URL if needed
        os.environ['DATABASE_URL'] = "postgresql://postgres:postgres@127.0.0.1:5435/shifty"
        await db.connect()
        user = await db.user.find_first(
            where={'email': 'eliran8hadad@gmail.com'},
            order={'createdAt': 'desc'}
        )
        if user:
            with open('output_code.txt', 'w') as f:
                f.write(f"EMAIL: {user.email}\nCODE: {user.verificationCode}\nVERIFIED: {user.isVerified}")
            print(f"Code found: {user.verificationCode}")
        else:
            print("User not found")
        await db.disconnect()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
