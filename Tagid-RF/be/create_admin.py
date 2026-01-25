import asyncio
from prisma import Prisma
from prisma.models import User, Business
from app.core.security import get_password_hash

async def main():
    db = Prisma()
    await db.connect()

    email = "eliran8hadad@gmail.com"
    phone = "972545486607"
    name = "Eliran Hadad"
    password = "1234"
    hashed_password = get_password_hash(password)

    print(f"Checking for user: {email}")

    # 1. Ensure a business exists
    business = await db.business.find_first()
    if not business:
        print("Creating default business...")
        business = await db.business.create(
            data={
                "name": "Columbus AH",
                "slug": "columbus-ah"
            }
        )
    
    # 2. Find or create user
    user = await db.user.find_unique(where={"email": email})
    
    if user:
        print(f"User found. Updating permissions and password...")
        user = await db.user.update(
            where={"id": user.id},
            data={
                "role": "SUPER_ADMIN",
                "phone": phone,
                "name": name,
                "password": hashed_password,
                "receiveTheftAlerts": True
            }
        )
    else:
        print(f"Creating new SUPER_ADMIN user...")
        user = await db.user.create(
            data={
                "email": email,
                "name": name,
                "phone": phone,
                "address": "Israel",
                "password": hashed_password,
                "role": "SUPER_ADMIN",
                "businessId": business.id,
                "receiveTheftAlerts": True
            }
        )

    print(f"✓ Success! User {user.email} is now a SUPER_ADMIN.")
    print(f"Details: ID={user.id}, Role={user.role}, Password=1234")

    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
