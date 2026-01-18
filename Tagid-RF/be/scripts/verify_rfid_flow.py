import asyncio
import websockets
import json


async def test_rfid_websocket():
    uri = "ws://localhost:8000/ws/rfid"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Successfully connected to WebSocket.")

            # Wait for welcome message
            welcome = await websocket.recv()
            print(f"Received: {welcome}")

            # Wait for some tag scans (simulation mode should be active)
            print("Waiting for tag scans (simulation mode)...")
            for _ in range(3):
                message = await websocket.recv()
                data = json.loads(message)
                if data.get("type") == "tag_scanned":
                    tag = data["data"]
                    print(
                        f"Tag Scanned: EPC={tag['epc']}, RSSI={tag['rssi']}, Location={tag['location']}"
                    )
                else:
                    print(f"Received other message: {data}")

            print("Test completed successfully.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_rfid_websocket())
