import asyncio
from app.db.prisma import prisma_client
from app.services.theft_detection import TheftDetectionService
from prisma.enums import Role, ReaderType
from app.core.security import get_password_hash

async def simulate_theft():
    print("🚀 Starting Theft Simulation...")
    
    try:
        await prisma_client.connect()
        
        # --- PHASE 1: User & Subscription Setup ---
        print("\n[1/4] Setting up User & Subscriptions...")
        
        # Ensure Business Exists
        biz = await prisma_client.client.business.find_first()
        if not biz:
            print("   Creating default business...")
            biz = await prisma_client.client.business.create(
                data={"name": "Test Biz", "slug": "test-biz"}
            )
        
        # Try to find user
        email = "demo@example.com"
        user = await prisma_client.client.user.find_unique(where={"email": email})
        
        if not user:
            print("   Creating Admin User...")
            user = await prisma_client.client.user.create(
                data={
                    "email": email,
                    "password": get_password_hash("password"),
                    "name": "Demo Admin",
                    "phone": "1234567890",
                    "address": "123 Test St",
                    "role": Role.SUPER_ADMIN, 
                    "receiveTheftAlerts": True,
                    "businessId": biz.id
                }
            )
        else:
            print(f"   Found existing user: {user.email}")
            # Upgrade user to Admin causing them to get alerts
            await prisma_client.client.user.update(
                where={"id": user.id},
                data={
                    "role": Role.SUPER_ADMIN,
                    "receiveTheftAlerts": True
                }
            )
            print("   User updated to SUPER_ADMIN with Alerts ON.")

        # Link Subscriptions to this User
        # We find all subscriptions and link them to this user to ensure the demo works
        updated_subs = await prisma_client.client.pushsubscription.update_many(
            where={},
            data={"userId": user.id}
        )
        print(f"   Linked {updated_subs} push subscriptions to user {user.id}")


        # --- PHASE 2: Reader Setup ---
        print("\n[2/4] Setting up GATE Reader...")
        reader_ip = "10.0.0.99"
        reader = await prisma_client.client.rfidreader.find_unique(where={"ipAddress": reader_ip})
        
        if not reader:
            reader = await prisma_client.client.rfidreader.create(
                data={
                    "name": "Exit Gate 1",
                    "ipAddress": reader_ip,
                    "type": ReaderType.GATE,
                    "location": "Main Exit"
                }
            )
            print(f"   Created Reader: {reader.name}")
        else:
             # Ensure it's a GATE
            if reader.type != ReaderType.GATE:
                 await prisma_client.client.rfidreader.update(
                    where={"id": reader.id},
                    data={"type": ReaderType.GATE}
                 )
            print(f"   Using Reader: {reader.name} (GATE)")


        # --- PHASE 3: Tag Setup ---
        print("\n[3/4] Creating Unpaid Tag...")
        test_epc = "E20000199999026318905445"
        
        # Check if exists, delete to reset or update
        existing_tag = await prisma_client.client.rfidtag.find_unique(where={"epc": test_epc})
        
        if existing_tag:
             await prisma_client.client.rfidtag.update(
                where={"epc": test_epc},
                data={"isPaid": False}
             )
             tag = existing_tag
        else:
             tag = await prisma_client.client.rfidtag.create(
                 data={
                     "epc": test_epc,
                     "productDescription": "Premium Leather Jacket",
                     "isPaid": False
                 }
             )
        print(f"   Tag Ready: {tag.epc} (Paid: {tag.isPaid})")


        # --- PHASE 4: Trigger Theft Detection ---
        print("\n[4/4] 🕵️‍♂️ Simulating Theft Event...")
        
        service = TheftDetectionService()
        
        # This checks the tag status. Since it's unpaid, it should trigger the alert logic
        # defined in TheftDetectionService._create_theft_alert -> _notify_stakeholders
        is_paid = await service.check_tag_payment_status(
            epc=test_epc,
            location=f"{reader.name} ({reader.ipAddress})"
        )
        
        if not is_paid:
            print("\n✅ Theft Detected & Notification Sent!")
            print("👉 Check your screen/browser for the push notification.")
        else:
            print("\n❌ Warning: Service reported tag as PAID (No theft detected).")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await prisma_client.disconnect()

if __name__ == "__main__":
    asyncio.run(simulate_theft())
