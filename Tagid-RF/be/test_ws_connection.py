
import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://localhost:8000/ws/rfid"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            welcome = await websocket.recv()
            print(f"Server says: {welcome}")
            
            # Subscribe
            await websocket.send(json.dumps({"command": "subscribe"}))
            print("Sent subscribe command")
            
            response = await websocket.recv()
            print(f"Server response: {response}")
            
            print("WS Test Passed ✅")
    except Exception as e:
        print(f"Connection failed ❌: {e}")

if __name__ == "__main__":
    asyncio.run(test_ws())
