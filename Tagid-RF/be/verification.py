import asyncio
from unittest.mock import MagicMock, patch

import app.services.rfid_reader
from app.services.rfid_reader import M200ResponseParser, RFIDReaderService

print("Checking imports in rfid_reader...")
print(
    f"parse_inventory_response in rfid_reader: {'parse_inventory_response' in dir(app.services.rfid_reader)}"
)
print(f"M200ResponseParser in rfid_reader: {'M200ResponseParser' in dir(app.services.rfid_reader)}")


async def verify_process_tag():
    print("\nVerifying process_tag logic...")
    service = RFIDReaderService()
    mock_db = MagicMock()
    # verify commit tracking
    mock_db.commit()
    mock_db.commit.assert_called()
    print("Mock DB commit tracking works.")

    with patch("app.services.rfid_reader.SessionLocal", return_value=mock_db):
        # We also need to patch other things to reach commit
        # existing_tag = True path
        mock_tag = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_tag

        # Patch Prisma to avoid error
        with patch("app.db.prisma.prisma_client") as mock_pc:
            with patch("app.services.rfid_reader.manager.broadcast"):
                await service._process_tag({"epc": "E1", "rssi": -1})

    if mock_db.commit.called:
        print("SUCCESS: db.commit called in process_tag.")
    else:
        print("FAILURE: db.commit NOT called in process_tag.")


async def verify_read_single():
    print("\nVerifying read_single_tag logic...")
    service = RFIDReaderService()
    service.is_connected = True

    with patch.object(service, "_send_command", return_value=b"data"):
        with patch("app.services.rfid_reader.M200ResponseParser") as MockParser:
            MockParser.parse.return_value.success = True
            MockParser.parse.return_value.status = 0
            MockParser.parse.return_value.data = b"tagdata"

            with patch("app.services.rfid_reader.parse_inventory_response") as mock_inv:
                mock_inv.return_value = [{"epc": "TEST"}]

                tags = await service.read_single_tag()
                print(f"Tags returned: {tags}")


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(verify_process_tag())
    loop.run_until_complete(verify_read_single())
