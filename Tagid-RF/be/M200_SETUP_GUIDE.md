# M-200 Gate Reader Setup Guide

## ✅ **Protocol Implementation Complete**

The M-200 uses a **custom protocol** that is incompatible with standard Chafon CF-RU readers. I've implemented the full M-200 protocol based on the official manual.

## 📋 **What's New**

### 1. **M-200 Protocol Module** (`app/services/m200_protocol.py`)

Complete implementation of M-200 communication protocol:
- ✅ CRC16 checksum calculation (Appendix B)
- ✅ Command frame builder
- ✅ Response frame parser
- ✅ All command codes from manual
- ✅ Device info parsing
- ✅ Tag inventory parsing

### 2. **Updated RFID Reader Service** (`app/services/rfid_reader.py`)

Refactored to use M-200 native protocol:
- ✅ TCP/IP socket communication
- ✅ Device information retrieval
- ✅ Tag inventory (single & continuous)
- ✅ Proper error handling
- ✅ Database integration
- ✅ WebSocket broadcasting

### 3. **Removed Dependencies**

- ❌ Removed `wabson.chafon-rfid` (incompatible)
- ❌ Removed `anyio` (not needed)
- ❌ Removed `pyserial` (TCP only for now)

## 🚀 **Quick Start**

### Step 1: Install Dependencies

```bash
cd be
pip install -r requirements.txt
```

### Step 2: Configure M-200 Network

**Option A: Set Static IP on M-200** (Recommended)

1. Access M-200 web interface or use configuration tool
2. Set static IP in your network range:
   ```
   IP: 192.168.1.100
   Subnet: 255.255.255.0
   Gateway: 192.168.1.1
   ```

**Option B: Use Link-Local IP** (Current: `169.254.128.161`)

If keeping link-local, configure your computer:
```bash
# macOS
sudo ifconfig en0 alias 169.254.128.162 netmask 255.255.0.0

# Linux
sudo ip addr add 169.254.128.162/16 dev eth0

# Windows
netsh interface ip add address "Ethernet" 169.254.128.162 255.255.0.0
```

### Step 3: Update `.env`

```env
# M-200 Configuration
RFID_READER_IP=169.254.128.161  # Or your static IP
RFID_READER_PORT=4001
RFID_SOCKET_TIMEOUT=10
RFID_READER_ID=M200-001
LOG_LEVEL=INFO
```

### Step 4: Test Connection

```bash
# Start backend
uvicorn app.main:app --reload

# In another terminal, test connection
curl -X POST http://localhost:8000/api/v1/tags/reader/connect

# Expected response:
# {"status": "connected", "message": "..."}
```

### Step 5: Get Device Info

```bash
curl http://localhost:8000/api/v1/tags/reader/status

# Expected response:
# {
#   "connected": true,
#   "model": "M-200",
#   "reader_type": "M-Series Gate Reader",
#   "serial_number": "...",
#   "rfid_firmware_version": "...",
#   ...
# }
```

### Step 6: Read Tags

```bash
# Single read
curl -X POST http://localhost:8000/api/v1/tags/reader/read-single

# Start continuous scanning
curl -X POST http://localhost:8000/api/v1/tags/reader/start-scan

# Stop scanning
curl -X POST http://localhost:8000/api/v1/tags/reader/stop-scan
```

## 📡 **M-200 Protocol Details**

### Command Frame Format

```
[ADDR][CMD][LEN_H][LEN_L][DATA...][CRC_L][CRC_H]
```

- **ADDR**: Device address (1 byte, default 0x00)
- **CMD**: Command code (1 byte)
- **LEN**: Data length (2 bytes, big-endian)
- **DATA**: Command payload (variable)
- **CRC**: CRC16 checksum (2 bytes, little-endian)

### Response Frame Format

```
[ADDR][CMD][STATUS][LEN_H][LEN_L][DATA...][CRC_L][CRC_H]
```

- **STATUS**: 0x00 = success, other = error code

### Key Commands Implemented

| Command | Code | Description |
|---------|------|-------------|
| `RFM_GET_DEVICE_INFO` | 0x21 | Get device information |
| `RFM_INVENTORYISO_CONTINUE` | 0x27 | Start tag inventory |
| `RFM_INVENTORY_STOP` | 0x28 | Stop tag inventory |
| `RFM_READISO_TAG` | 0x2A | Read tag data |
| `RFM_SET_PWR` | 0x2F | Set RF power |

See `app/services/m200_protocol.py` for full command list.

### Tag Inventory Response

Each tag in response contains:
- **RSSI**: Signal strength (1 byte, negative dBm)
- **Ant**: Antenna number (1 byte)
- **PC**: Protocol control (2 bytes)
- **EPC Length**: EPC data length (1 byte)
- **EPC Data**: Tag EPC (variable)

## 🔧 **Advanced Configuration**

### Adjust Socket Timeout

If M-200 is slow to respond:
```env
RFID_SOCKET_TIMEOUT=30  # Increase to 30 seconds
```

### Enable Debug Logging

See detailed protocol communication:
```env
LOG_LEVEL=DEBUG
```

You'll see:
```
→ TX: 0021000000004E21  (Command sent)
← RX: 002100001800...    (Response received)
```

### Configure RF Power

Add to your initialization code:
```python
from app.services.m200_protocol import M200Command, M200Commands

# Set power to 26 dBm
cmd = M200Command(M200Commands.RFM_SET_PWR, bytes([26, 0x00]))
response = await rfid_reader_service._send_command(cmd)
```

## 🐛 **Troubleshooting**

### Issue: Connection Timeout

**Symptoms**: `socket.timeout: timed out`

**Solutions**:
1. Verify M-200 IP with `ping 169.254.128.161`
2. Check port with `telnet 169.254.128.161 4001`
3. Increase timeout in `.env`
4. Check M-200 TCP server is enabled

### Issue: CRC Mismatch

**Symptoms**: `ValueError: CRC mismatch`

**Solutions**:
1. Check for network interference
2. Verify M-200 firmware version
3. Enable debug logging to see raw bytes

### Issue: No Tags Detected

**Symptoms**: Empty response from read-single

**Solutions**:
1. Ensure tag is within range (0-10m for M-200)
2. Check RF power setting
3. Verify antenna connection
4. Try different tag (might be damaged)

### Issue: Invalid Frame Length

**Symptoms**: `ValueError: Frame too short` or `Invalid frame length`

**Solutions**:
1. Check network stability
2. Increase socket timeout
3. Verify M-200 firmware compatibility

## 📊 **Performance Tips**

### Optimize Scan Rate

```python
# In _scan_loop, adjust delay:
await asyncio.sleep(0.1)  # 10 scans/second (default)
await asyncio.sleep(0.05) # 20 scans/second (faster)
await asyncio.sleep(0.2)  # 5 scans/second (slower, less CPU)
```

### Filter Duplicate Reads

Use M-200's built-in filter (Section 2.2.8):
```python
# Set filter time to 5 seconds
# Tags with same EPC filtered for 5s after first read
# (Requires implementing RFM_SET_ALL_PARAM command)
```

### Use Multiple Antennas

If your M-200 has multiple antenna ports:
```python
# Configure antenna mask (Section 2.2.8)
# Ant parameter: bit mask for antennas 1-8
# 0x01 = Antenna 1 only
# 0x03 = Antennas 1 & 2
# 0x0F = Antennas 1-4
```

## 🔐 **Security Notes**

1. **Network Isolation**: Keep M-200 on isolated VLAN
2. **Access Control**: Use firewall rules to restrict port 4001
3. **Authentication**: M-200 doesn't have built-in auth, secure at network level

## 📚 **Additional Resources**

- **Manual**: `be/CF-M Gate Reader User ManualV1.txt`
- **Protocol Module**: `be/app/services/m200_protocol.py`
- **Service**: `be/app/services/rfid_reader.py`
- **API Endpoints**: `be/app/routers/tags.py`

## ✅ **Testing Checklist**

- [ ] M-200 has proper network configuration
- [ ] Can ping M-200 IP address
- [ ] Port 4001 is accessible (telnet test)
- [ ] Backend connects successfully
- [ ] Device info retrieval works
- [ ] Single tag read works
- [ ] Continuous scanning works
- [ ] Tags saved to database
- [ ] WebSocket broadcasts working

## 🎯 **Next Steps**

1. **Test Connection**: Follow Quick Start above
2. **Verify Tag Reading**: Place tag near M-200 and test
3. **Configure Frontend**: Update frontend to display scanned tags
4. **Implement Additional Commands**: Add more M-200 features as needed

---

**Status**: ✅ **Ready for Testing**

The M-200 protocol is fully implemented and ready to use. Just configure the network and start scanning!

