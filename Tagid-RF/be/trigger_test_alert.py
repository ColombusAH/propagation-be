import asyncio
import uuid
from prisma import Prisma
from app.services.push_notification_service import PushNotificationService

async def main():
    db = Prisma()
    await db.connect()

    print("Preparing test tag...")
    
    # Create a test tag (RfidTag model doesn't have businessId in this schema)
    epc = "TEST_EPC_" + uuid.uuid4().hex[:8]
    tag = await db.rfidtag.create(
        data={
            "epc": epc,
            "productDescription": "פריט בדיקה למניעת גניבות",
            "status": "UNREGISTERED",
            "isPaid": False
        }
    )
    
    print(f"Triggering test theft alert for tag: {epc}...")
    
    service = PushNotificationService(db)
    
    # This will create an alert and notify all users with receiveTheftAlerts=True
    result = await service.send_theft_alert(
        tag_id=tag.id,
        epc=epc,
        location="שער יציאה ראשי - בדיקה",
    )
    
    print(f"✓ Test alert created! ID: {result['alert_id']}")
    print(f"Notified {result['recipients_notified']} users.")

    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
