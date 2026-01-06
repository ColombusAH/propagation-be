# M200 UHF Reader Compatibility Guide

## 📋 Status: **Likely Compatible** ⚠️

The Chafon M200 UHF reader is **not officially listed** in the `wabson.chafon-rfid` library, but it will likely work since most Chafon UHF readers use similar protocols.

## ✅ **Compatibility Factors**

| Factor | Status | Notes |
|--------|--------|-------|
| **Protocol** | ✅ Likely Compatible | Most Chafon UHF use ISO18000-6C (EPC Gen2) |
| **Connection** | ✅ Supported | TCP/IP and Serial both supported |
| **Auto-Detection** | ✅ Yes | Library auto-detects reader type |
| **Official Support** | ⚠️ Not Listed | M200 not in official device list |

## 🧪 **Testing Steps**

### Step 1: Try Standard Configuration

```env
# .env configuration for M200
RFID_CONNECTION_TYPE=tcp
RFID_READER_IP=192.168.1.100  # Your M200's IP
RFID_READER_PORT=4001
RFID_READER_ID=M200-001
```

### Step 2: Test Connection

```bash
# Install dependencies
pip install wabson.chafon-rfid anyio

# Start server
uvicorn app.main:app --reload

# Test connection
curl -X POST http://localhost:8000/api/v1/tags/reader/connect
```

### Step 3: Check Reader Info

```bash
# This will show detected reader type
curl http://localhost:8000/api/v1/tags/reader/status
```

**Expected Output:**
```json
{
  "connected": true,
  "reader_type": "UHFReader18",  // or UHFReader288M, etc.
  "firmware_version": "...",
  "model": "M200",
  "ip": "192.168.1.100"
}
```

### Step 4: Test Tag Reading

```bash
# Try reading a single tag
curl -X POST http://localhost:8000/api/v1/tags/reader/read-single
```

## 🔧 **If Standard Config Doesn't Work**

### Option 1: Try Alternative Frame Class

If you get parsing errors, the M200 might use a different response frame format.

**Edit `app/services/rfid_reader.py`:**

```python
# Line ~170 - Change from:
from chafon_rfid.uhfreader18 import G2InventoryResponseFrame as G2InventoryResponseFrame18

# To:
from chafon_rfid.uhfreader288m import G2InventoryResponseFrame as G2InventoryResponseFrame288
```

**Then change line ~190:**

```python
# From:
resp = G2InventoryResponseFrame18(raw)

# To:
resp = G2InventoryResponseFrame288(raw)
```

### Option 2: Use Generic ReaderType Detection

Add automatic frame selection based on detected reader type:

```python
def _get_frame_class(self):
    """Determine correct frame class based on reader type."""
    try:
        from chafon_rfid.base import ReaderCommand, ReaderInfoFrame, ReaderType
        from chafon_rfid.command import CF_GET_READER_INFO
        from chafon_rfid.uhfreader18 import G2InventoryResponseFrame as Frame18
        from chafon_rfid.uhfreader288m import G2InventoryResponseFrame as Frame288
        
        # Get reader info
        frame = self._runner.run(ReaderCommand(CF_GET_READER_INFO))
        info = ReaderInfoFrame(frame)
        
        # Select appropriate frame class
        if info.type in (ReaderType.UHFReader288M, ReaderType.UHFReader288MP):
            return Frame288
        else:
            return Frame18
            
    except Exception as e:
        logger.warning(f"Could not detect reader type, using default: {e}")
        from chafon_rfid.uhfreader18 import G2InventoryResponseFrame as Frame18
        return Frame18
```

## 📊 **Known Chafon Protocols**

Different Chafon readers use different response formats:

| Reader Family | Frame Class | Notes |
|---------------|-------------|-------|
| **CF-RU5102** | `G2InventoryResponseFrame18` | Desktop USB reader |
| **CF-001-548** | `G2InventoryResponseFrame18` | Current implementation |
| **CF-MU801/804** | `G2InventoryResponseFrame288` | Impinj R2000 modules |
| **CF-MU904** | `G2InventoryResponseFrame288` | UHF module |
| **M200** | `❓ Unknown` | **Need to test** |

## 🔍 **Diagnostic Steps**

### Enable Debug Logging

Add to `.env`:
```env
LOG_LEVEL=DEBUG
```

This will show:
- Raw command bytes sent
- Raw response bytes received
- Parsing details
- Connection info

### Check Logs

```bash
# Watch logs when connecting
tail -f logs/app.log

# Or check terminal output
# Look for:
# - "Connected to RFID reader"
# - "Reader type: ..."
# - Any parsing errors
```

### Common Error Messages

| Error | Likely Cause | Solution |
|-------|--------------|----------|
| `Connection refused` | Wrong IP/Port | Check M200 network settings |
| `TableNotFoundError` | Database not initialized | Run `python scripts/db.py deploy` |
| `Frame parsing error` | Wrong frame class | Try `G2InventoryResponseFrame288` |
| `No tags detected` | Tag out of range | Move tag closer (0-20m) |

## 📝 **M200 Specifications to Check**

If available, check your M200 manual for:

1. **Protocol Version**: ISO18000-6C / EPC Gen2 (should be compatible)
2. **Communication Protocol**: Does it use Chafon standard protocol?
3. **Default Port**: Usually 4001, but verify
4. **Response Format**: Which frame type (18 or 288)?
5. **Chipset**: Impinj R2000 or proprietary?

## ✉️ **Reporting Results**

If you test with M200, please note:

- ✅ **Works perfectly** → Use as-is
- ⚠️ **Works with modifications** → Document what you changed
- ❌ **Doesn't work** → May need custom implementation

## 🔗 **Alternative: Direct Protocol Implementation**

If the library doesn't support M200, you can:

1. **Find M200 protocol documentation** from Chafon
2. **Implement custom commands** using library's base classes
3. **Create M200-specific frame parser** inheriting from `ReaderResponseFrame`

Example:
```python
from chafon_rfid.base import ReaderResponseFrame

class M200ResponseFrame(ReaderResponseFrame):
    def __init__(self, resp_bytes):
        super().__init__(resp_bytes)
        # Custom parsing for M200
```

## 📚 **Resources**

- **Library GitHub**: https://github.com/wabson/chafon-rfid
- **Chafon Website**: http://www.chafon.com/
- **Protocol Docs**: Request from Chafon support
- **Issue Tracker**: Report M200 compatibility issues

## 💡 **Recommendation**

1. **Try it first** with standard configuration
2. **Check logs** for any errors
3. **Try Frame288** if Frame18 fails
4. **Contact Chafon** if neither works
5. **Open GitHub issue** on wabson/chafon-rfid if M200 needs support

---

**TL;DR**: The M200 **should work** with the current implementation since it's a Chafon UHF reader. If not, you'll likely only need to change the frame class from `G2InventoryResponseFrame18` to `G2InventoryResponseFrame288`. Test it and check the logs!

