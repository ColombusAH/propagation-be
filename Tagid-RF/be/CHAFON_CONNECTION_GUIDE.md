# Chafon CF-001-548 Connection Guide

Complete guide for connecting your Chafon CF-001-548 RFID reader via Ethernet/TCP and reading tags.

## 📋 Prerequisites

- Chafon CF-001-548 UHF RFID Reader
- Ethernet cable connected to the device (for TCP connection)
- **OR** USB/Serial cable (for serial connection)
- Device configured with a static IP address (or DHCP with known IP) if using TCP
- Backend server running and accessible
- `wabson.chafon-rfid` library installed

## 🔧 Step 1: Configure Device IP Address

### For TCP/IP (Ethernet) Connection

Find your device's IP address:

1. **Check the device display** - The CF-001-548 may show its IP on the home screen
2. **Check your router** - Look for connected devices in your router's admin panel
3. **Use network scanner** - Scan your local network for the device

### Set Static IP (Recommended)

If your device uses DHCP, configure a static IP:

1. Access device settings (usually via Settings > Network > Ethernet)
2. Set a static IP in your local network range (e.g., `192.168.1.100`)
3. Set subnet mask: `255.255.255.0`
4. Set gateway: Your router IP (e.g., `192.168.1.1`)
5. Note the port number (default is usually `4001` for Chafon devices)

## ⚙️ Step 2: Configure Backend Settings

Edit your `.env` file in the `be/` directory:

### For TCP/IP (Ethernet) Connection:

```env
# RFID Reader Configuration
RFID_READER_IP=192.168.1.100        # Your device's IP address
RFID_READER_PORT=4001                # Default Chafon port (adjust if needed)
RFID_CONNECTION_TYPE=tcp             # Use 'tcp' for Ethernet/WiFi connection
RFID_READER_ID=CF-001-548            # Unique identifier for this reader
```

### For Serial/USB Connection:

```env
# RFID Reader Configuration
RFID_CONNECTION_TYPE=serial          # Use 'serial' for USB/RS232 connection
RFID_SERIAL_DEVICE=/dev/ttyUSB0      # Linux/Mac: /dev/ttyUSB0 or /dev/ttyACM0
                                      # Windows: COM3 or COM4
RFID_READER_ID=CF-001-548            # Unique identifier for this reader
```

**Important**: 
- For TCP: Replace `192.168.1.100` with your actual device IP address
- For Serial: Replace `/dev/ttyUSB0` with your actual serial port

## 🚀 Step 3: Install Dependencies

First, install the chafon-rfid library:

```bash
cd be
source myenv/bin/activate  # Activate virtual environment
pip install wabson.chafon-rfid anyio
```

## 🚀 Step 4: Start the Backend Server

```bash
cd be
source myenv/bin/activate  # Activate virtual environment
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔌 Step 5: Connect to the Device

### Option A: Using API Endpoint (Recommended)

**Connect to the reader:**
```bash
curl -X POST http://localhost:8000/api/v1/tags/reader/connect
```

**Expected Response:**
```json
{
  "status": "connected",
  "message": "Successfully connected to RFID reader at 192.168.1.100:4001",
  "reader_info": {
    "connected": true,
    "model": "CF-H906",
    "ip": "192.168.1.100",
    "port": 4001,
    "reader_id": "CF-H906-001",
    "connection_type": "wifi"
  }
}
```

### Option B: Using Swagger UI

1. Open http://localhost:8000/docs
2. Find `POST /api/v1/tags/reader/connect`
3. Click "Try it out" → "Execute"
4. Check the response

### Check Connection Status

```bash
curl http://localhost:8000/api/v1/tags/reader/status
```

## 📡 Step 6: Read Tags

### Read a Single Tag (One-Time Scan)

```bash
curl -X POST http://localhost:8000/api/v1/tags/reader/read-single
```

**Response when tag is detected:**
```json
{
  "status": "success",
  "tag": {
    "epc": "E200001234567890ABCDEF01",
    "rssi": -45,
    "antenna_port": 1,
    "timestamp": "2024-12-13T10:30:00Z"
  }
}
```

**Response when no tag detected:**
```json
{
  "status": "no_tag",
  "message": "No tag detected. Try moving a tag closer to the reader."
}
```

### Start Continuous Scanning

```bash
curl -X POST http://localhost:8000/api/v1/tags/reader/start-scanning
```

This will:
- Continuously scan for tags
- Automatically save tags to the database
- Broadcast tags via WebSocket in real-time

### Stop Scanning

```bash
curl -X POST http://localhost:8000/api/v1/tags/reader/stop-scanning
```

## 👀 Step 7: View Scanned Tags

### View All Tags

```bash
curl http://localhost:8000/api/v1/tags
```

### View Recent Scans

```bash
curl http://localhost:8000/api/v1/tags/recent/scans?hours=1&limit=50
```

### View Statistics

```bash
curl http://localhost:8000/api/v1/tags/stats/summary
```

## 🔴 Step 8: Real-Time Monitoring via WebSocket

Connect to the WebSocket endpoint for real-time tag notifications:

### JavaScript Example

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/rfid');

ws.onopen = () => {
  console.log('Connected to RFID stream');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'tag_scanned') {
    console.log('Tag scanned:', data.data);
    console.log('EPC:', data.data.epc);
    console.log('RSSI:', data.data.rssi);
    console.log('Timestamp:', data.data.timestamp);
  } else if (data.type === 'welcome') {
    console.log('Welcome message:', data.message);
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket disconnected');
};
```

### Python Example

```python
import asyncio
import websockets
import json

async def listen_for_tags():
    uri = "ws://localhost:8000/ws/rfid"
    async with websockets.connect(uri) as websocket:
        # Send ping
        await websocket.send(json.dumps({"command": "ping"}))
        
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            if data.get("type") == "tag_scanned":
                print(f"Tag scanned: {data['data']['epc']}")
                print(f"RSSI: {data['data']['rssi']} dBm")
            elif data.get("type") == "welcome":
                print(f"Connected: {data['message']}")

asyncio.run(listen_for_tags())
```

## 🛠️ Troubleshooting

### Connection Failed

**Error**: `Connection failed: [Errno 61] Connection refused`

**Solutions**:
1. **Check device IP address** - Verify the IP in `.env` matches your device
2. **Ping the device**:
   ```bash
   ping 192.168.1.100  # Replace with your device IP
   ```
3. **Check port** - Verify the port number (default is 4001)
4. **Check firewall** - Ensure port 4001 is not blocked
5. **Check Ethernet connection** - Ensure cable is properly connected

### No Tags Detected

**Solutions**:
1. **Move tag closer** - UHF tags need to be within range (0-20 meters)
2. **Check tag frequency** - Ensure tag is UHF (860-960MHz)
3. **Check reader power** - Increase power level if configurable
4. **Try different tags** - Some tags may not be compatible

### Protocol Errors

**Error**: Protocol or parsing errors

**Solutions**:
1. **Check library compatibility** - Ensure `wabson.chafon-rfid` is properly installed
2. **Enable debug logging** - Set `LOG_LEVEL=DEBUG` in `.env` to see raw responses
3. **Check reader model** - The CF-001-548 uses the UHFReader18 protocol
4. **Verify imports** - Check that all chafon_rfid imports are correct

### Library Import Errors

**Error**: `ModuleNotFoundError: No module named 'chafon_rfid'`

**Solutions**:
1. **Install the library**:
   ```bash
   pip install wabson.chafon-rfid
   ```
2. **Check virtual environment** - Ensure you're in the correct venv
3. **Restart the server** after installing the library

### Device Not Responding

**Solutions**:
1. **Restart the device** - Power cycle the CF-H906
2. **Check network settings** - Verify IP, subnet, gateway
3. **Test with telnet**:
   ```bash
   telnet 192.168.1.100 4001
   ```
4. **Check device logs** - Review device error messages

## 📝 API Reference

### Reader Control Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/tags/reader/connect` | Connect to RFID reader |
| POST | `/api/v1/tags/reader/disconnect` | Disconnect from reader |
| POST | `/api/v1/tags/reader/start-scanning` | Start continuous scanning |
| POST | `/api/v1/tags/reader/stop-scanning` | Stop scanning |
| GET | `/api/v1/tags/reader/status` | Get reader status |
| POST | `/api/v1/tags/reader/read-single` | Read a single tag (one-time) |

### Tag Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/tags` | List all tags |
| GET | `/api/v1/tags/{id}` | Get tag by ID |
| GET | `/api/v1/tags/epc/{epc}` | Get tag by EPC |
| GET | `/api/v1/tags/recent/scans` | Get recent scan history |
| GET | `/api/v1/tags/stats/summary` | Get statistics |

### WebSocket

- **Endpoint**: `ws://localhost:8000/ws/rfid`
- **Events**: `tag_scanned`, `welcome`, `pong`

## 🔍 Testing Connection

### Quick Test Script

```bash
#!/bin/bash

# Set your device IP
DEVICE_IP="192.168.1.100"
API_URL="http://localhost:8000/api/v1/tags"

echo "1. Testing connection..."
curl -X POST "$API_URL/reader/connect"

echo -e "\n\n2. Checking status..."
curl "$API_URL/reader/status"

echo -e "\n\n3. Reading a single tag (place tag near reader)..."
curl -X POST "$API_URL/reader/read-single"

echo -e "\n\n4. Starting continuous scan..."
curl -X POST "$API_URL/reader/start-scanning"

echo -e "\n\n5. Waiting 5 seconds for tags..."
sleep 5

echo -e "\n\n6. Stopping scan..."
curl -X POST "$API_URL/reader/stop-scanning"

echo -e "\n\n7. Viewing scanned tags..."
curl "$API_URL?page=1&page_size=10"

echo -e "\n\nDone!"
```

## 📚 Additional Resources

- [Chafon CF-H906 Documentation](https://www.chafon.com/) - Official device documentation
- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [RFID README](./RFID_README.md) - Complete system documentation

## ⚠️ Important Notes

1. **Library Integration**: This implementation uses the official `wabson.chafon-rfid` library for proper hardware communication.

2. **Connection Types**:
   - **TCP/IP** (Recommended): For Ethernet or WiFi connections
   - **Serial**: For direct USB or RS232 connections

3. **Network Requirements** (TCP only): 
   - Device and server must be on the same network
   - Port 4001 must be accessible
   - No firewall blocking TCP connections

4. **Serial Requirements** (Serial only):
   - Proper serial drivers installed
   - User has permissions to access serial port (Linux: add user to `dialout` group)
   - Correct serial device path configured

5. **Performance**: 
   - CF-001-548 can read up to 200 tags/second
   - Continuous scanning uses ~20 reads/second to balance performance
   - Adjust `asyncio.sleep()` delay in `_scan_loop()` if needed

6. **Tag Compatibility**: 
   - Supports ISO18000-6C (EPC Gen2) tags
   - Frequency: 860-960MHz UHF
   - Reading distance: 0-20 meters (depends on tag and environment)

7. **Async Bridge**: Uses `anyio` for async-to-sync bridging since the chafon-rfid library uses synchronous I/O

## 🆘 Need Help?

If you encounter issues:
1. Check the backend logs for detailed error messages
2. Enable debug logging: `LOG_LEVEL=DEBUG` in `.env`
3. Verify network connectivity with `ping` and `telnet`
4. Review device documentation for protocol specifics
5. Check that database tables exist (run migrations if needed)

