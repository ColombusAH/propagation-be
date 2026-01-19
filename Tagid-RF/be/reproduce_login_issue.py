
import asyncio
import logging
from prisma import Prisma
from app.crud.user import get_user_by_email, create_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def reproduce():
    db = Prisma()
    await db.connect()
    
    role = "SUPER_ADMIN"
    email = f"dev_super_admin@example.com"
    prisma_role = "SUPER_ADMIN"
    
    try:
        logger.info("Step 1: Cleaning up existing dev business")
        await db.business.delete_many(where={"name": "Dev Business"})
        
        logger.info("Step 2: Creating fresh dev business")
        # Explicit slug provided
        business = await db.business.create(
            data={
                "name": "Dev Business",
                "slug": "debug-slug-" + str(asyncio.get_event_loop().time()).split('.')[0]
            }
        )
        logger.info(f"Created Business: {business.id}")

        logger.info("Step 3: Checking for existing user")
        user = await get_user_by_email(db, email)
        
        if not user:
            logger.info("Step 4: Creating dev user")
            user = await create_user(
                db=db,
                email=email,
                password="devpassword",
                name=f"Dev {role.title()}",
                phone="000-000-0000",
                address="Dev Environment",
                business_id=business.id,
                role=prisma_role,
            )
            logger.info(f"Created User: {user.id}")
        else:
            logger.info(f"User already exists: {user.id}")
            
    except Exception as e:
        logger.error(f"Reproduction failed: {e}", exc_info=True)
    finally:
        await db.disconnect()

if __name__ == "__main__":
    asyncio.run(reproduce())
