# M-200 UHF Reader Troubleshooting Guide

## 🔴 **Current Issue: Socket Timeout**

**Error**: `socket.timeout: timed out` when sending commands

**Your IP**: `169.254.128.161:4001` (⚠️ Link-local address)

## 🎯 **Root Cause Analysis**

### Issue 1: Link-Local IP Address

The IP `169.254.128.161` is in the **link-local range** (169.254.0.0/16). This means:
- ❌ The device **couldn't get an IP from DHCP**
- ❌ Your computer and M-200 are **not properly networked**
- ⚠️ Link-local IPs are for **direct device-to-device** connection only

### Issue 2: Protocol Mismatch

The M-200 might use a **different command set** than standard Chafon readers.

## ✅ **Solutions**

### Solution 1: Fix Network Configuration (RECOMMENDED)

#### Option A: Static IP on M-200

1. **Access M-200 settings** (via device interface)
2. **Set Static IP**:
   - IP: `192.168.1.100` (or any valid IP in your network)
   - Subnet: `255.255.255.0`
   - Gateway: `192.168.1.1` (your router)
   - DNS: `8.8.8.8`

3. **Update `.env`**:
   ```env
   RFID_READER_IP=192.168.1.100
   ```

4. **Test connection**:
   ```bash
   ping 192.168.1.100
   ```

#### Option B: Configure Your Computer for Link-Local

If M-200 is fixed at link-local:

1. **Add link-local route**:
   ```bash
   # macOS/Linux
   sudo ifconfig en0 169.254.128.162 netmask 255.255.0.0
   
   # Windows
   netsh interface ip set address "Ethernet" static 169.254.128.162 255.255.0.0
   ```

2. **Test connection**:
   ```bash
   ping 169.254.128.161
   telnet 169.254.128.161 4001
   ```

### Solution 2: Increase Timeout

Add to `.env`:
```env
RFID_SOCKET_TIMEOUT=30  # Increase from default 10 seconds
LOG_LEVEL=DEBUG         # Enable detailed logging
```

### Solution 3: Test with Serial Connection

If TCP continues to fail, try USB/Serial:

```env
RFID_CONNECTION_TYPE=serial
RFID_SERIAL_DEVICE=/dev/ttyUSB0  # macOS: /dev/tty.usbserial-*
                                  # Windows: COM3
```

**Find serial port**:
```bash
# macOS
ls /dev/tty.*

# Linux
ls /dev/ttyUSB* /dev/ttyACM*

# Windows
mode
```

### Solution 4: Try Alternative Response Frame

If connection works but tag reading fails, the M-200 might use Frame288:

**Edit `app/services/rfid_reader.py` line ~178**:

```python
# Change from:
from chafon_rfid.uhfreader18 import G2InventoryResponseFrame as G2InventoryResponseFrame18

# To:
from chafon_rfid.uhfreader288m import G2InventoryResponseFrame as G2InventoryResponseFrame288
```

**Then line ~207**:
```python
# Change from:
resp = G2InventoryResponseFrame18(raw)

# To:
resp = G2InventoryResponseFrame288(raw)
```

## 🧪 **Diagnostic Tests**

### Test 1: Basic Network Connectivity

```bash
# Can you reach the device?
ping 169.254.128.161

# Is port 4001 open?
telnet 169.254.128.161 4001
# or
nc -zv 169.254.128.161 4001
```

**Expected**: Connection should succeed

### Test 2: Check M-200 Network Settings

Access M-200 device interface and check:
- IP Configuration (Static vs DHCP)
- Network interface status
- TCP Server enabled?
- Port number (might not be 4001)

### Test 3: Try Different Port

Some Chafon readers use different ports:

```env
RFID_READER_PORT=6000  # Try 6000
# or
RFID_READER_PORT=27011  # Try 27011
```

### Test 4: Raw Socket Test

Create a test script to verify M-200 protocol:

```python
import socket
import time

def test_m200(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    try:
        print(f"Connecting to {ip}:{port}...")
        sock.connect((ip, port))
        print("✓ Connected!")
        
        # Try sending a simple command (inventory)
        # Standard Chafon inventory: 0x04, 0xFF, 0x01, checksum
        cmd = bytes([0x04, 0xFF, 0x01, 0xFB, 0x04])
        print(f"Sending command: {cmd.hex()}")
        sock.sendall(cmd)
        
        # Try to receive response
        sock.settimeout(5)
        response = sock.recv(1024)
        print(f"✓ Received {len(response)} bytes: {response.hex()}")
        
        return True
    except socket.timeout:
        print("✗ Timeout - device not responding")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    finally:
        sock.close()

# Test your M-200
test_m200('169.254.128.161', 4001)
```

## 📊 **Common M-200 Issues**

| Symptom | Cause | Solution |
|---------|-------|----------|
| Connection refused | Wrong IP/Port | Verify M-200 settings |
| Timeout on commands | Protocol mismatch | Try Frame288 or check M-200 docs |
| Link-local IP | No DHCP | Configure static IP on M-200 |
| Connection succeeds, no response | Wrong command format | Check M-200 protocol documentation |

## 🔧 **M-200 Specific Configuration**

Based on testing, you may need:

```env
# .env for M-200
RFID_READER_IP=169.254.128.161  # Or static IP after config
RFID_READER_PORT=4001            # Verify with M-200 docs
RFID_CONNECTION_TYPE=tcp
RFID_SOCKET_TIMEOUT=30           # Longer timeout
RFID_READER_ID=M200-001
LOG_LEVEL=DEBUG                  # Enable debugging
```

## 📖 **What to Check in M-200 Documentation**

1. **TCP Server Port** - Is it really 4001?
2. **Protocol Version** - Standard Chafon or custom?
3. **Handshake Required?** - Some devices need initialization
4. **Response Format** - Frame18 or Frame288?
5. **Supported Commands** - Does it support `CF_GET_READER_INFO`?

## 🎬 **Next Steps**

1. **Fix Network First**:
   - Configure M-200 with proper static IP
   - OR configure your computer for link-local
   - Test with `ping` and `telnet`

2. **Restart Server**:
   ```bash
   # Stop current server (Ctrl+C)
   # Update .env with correct IP and timeout
   uvicorn app.main:app --reload
   ```

3. **Test Again**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/tags/reader/connect
   curl -X POST http://localhost:8000/api/v1/tags/reader/read-single
   ```

4. **Check Logs** for detailed error messages

## 💡 **Quick Wins**

Try these in order:

```bash
# 1. Increase timeout
echo "RFID_SOCKET_TIMEOUT=30" >> .env

# 2. Enable debug logging
echo "LOG_LEVEL=DEBUG" >> .env

# 3. Restart server and try again
```

## 📞 **If Still Not Working**

The M-200 may require:
- **Custom protocol implementation** (not using wabson.chafon-rfid)
- **M-200 specific SDK** from manufacturer
- **HTTP API** instead of TCP (some modern readers use REST APIs)
- **Android app bridge** if M-200 has Android SDK

Contact Chafon support for M-200 protocol documentation.

---

**Current Status**: Connection establishes but commands timeout → **Fix network configuration first!**

