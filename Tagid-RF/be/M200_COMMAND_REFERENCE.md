# M-200 Command Reference

Complete command list from **CF-M Gate Reader User Manual V1.2**

## ✅ **Implementation Status**

- ✅ **Implemented** - Ready to use
- 📝 **Helper Available** - Builder function exists
- ⏳ **Not Yet Implemented** - Command code defined, needs implementation

---

## 📋 **Command Summary**

| Category | Total Commands | Implemented | Percentage |
|----------|---------------|-------------|------------|
| General Control | 15 | 3 | 20% |
| ISO 18000-6C | 8 | 2 | 25% |
| GPIO Control | 2 | 0 | 0% |
| Gate Control | 3 | 0 | 0% |
| **TOTAL** | **28** | **5** | **18%** |

---

## 1️⃣ **Module General Control Commands** (Section 2.2)

### 1.1 RFM_MODULE_INT (0x0072) - Initialize Device
**Status**: ⏳ Not Implemented

**Purpose**: Initialize/reset the device

**Command Format**:
```
HEAD: 0xCF
ADDR: 0xFF
CMD:  0x0072
LEN:  0x00
DATA: (none)
CRC:  2 bytes
```

**Use Case**: Restart device after configuration changes

---

### 1.2 RFM_REBOOT (0x0070) - Factory Reset
**Status**: ⏳ Not Implemented

**Purpose**: Reset device to factory defaults

**Command Format**:
```
HEAD: 0xCF
ADDR: 0xFF
CMD:  0x0070
LEN:  0x00
DATA: (none)
CRC:  2 bytes
```

**Use Case**: Clear all settings and start fresh

---

### 1.3 RFM_SET_PWR (0x002F) - Set RF Output Power
**Status**: 📝 Helper Available - `build_set_power_command()`

**Purpose**: Configure RF transmission power

**Command Format**:
```
HEAD: 0xCF
ADDR: 0xFF
CMD:  0x002F
LEN:  0x01
DATA: [POWER] (1 byte, typically 0-30 dBm)
CRC:  2 bytes
```

**Example**:
```python
from app.services.m200_protocol import build_set_power_command

# Set power to 26 dBm
cmd = build_set_power_command(26)
response_bytes = await rfid_reader_service._send_command(cmd)
```

**Use Case**: Adjust read range (lower power = shorter range, less interference)

---

### 1.4 RFM_SET_GET_RFID_PRO (0x0041) - Set/Read RF Protocol
**Status**: ⏳ Not Implemented

**Purpose**: Configure which RFID protocols are supported

**Command Format**:
```
HEAD: 0xCF
ADDR: 0xFF
CMD:  0x0041
LEN:  0x02
DATA: [OPTION][PROTOCOL]
      OPTION: 0x01=Set, 0x02=Get
      PROTOCOL: 0x04=ISO18000-6C (EPC Gen2)
CRC:  2 bytes
```

**Use Case**: Ensure reader is in EPC Gen2 mode

---

### 1.5 RFM_SET_GET_NETPARA (0x0042) - Set/Read Network Settings
**Status**: ⏳ Not Implemented

**Purpose**: Configure device IP, subnet, gateway, port

**Command Format**:
```
HEAD: 0xCF
ADDR: 0xFF
CMD:  0x0042
LEN:  0x0D (set) or 0x01 (get)
DATA: [OPTION][IP][SUBNET][GATEWAY][PORT]
      OPTION: 0x01=Set, 0x02=Get
CRC:  2 bytes
```

**Use Case**: Set static IP address for M-200

---

### 1.6 RFM_SET_GET_REMOTE_NETPARA (0x0043) - Set/Read Remote Network Info
**Status**: ⏳ Not Implemented

**Purpose**: Configure remote server for data forwarding

**Use Case**: Send tag reads to remote server automatically

---

### 1.7 RFM_GET_DEVICE_INFO (0x0021) - Get Device Information ⭐
**Status**: ✅ **Implemented** - `get_reader_info()`

**Purpose**: Retrieve firmware version, serial number, hardware version

**Command Format**:
```
HEAD: 0xCF
ADDR: 0xFF
CMD:  0x0021
LEN:  0x00
DATA: (none)
CRC:  2 bytes
```

**Response Format**:
```
STATUS: 0x00 (success)
DATA:
  - CP Hardware Ver (2 bytes)
  - CP Firmware Ver (2 bytes)
  - RFID Hardware Ver (2 bytes)
  - RFID Firmware Ver (2 bytes)
  - Serial Number (16 bytes)
```

**Example**:
```python
info = await rfid_reader_service.get_reader_info()
print(f"Model: {info['model']}")
print(f"Serial: {info['serial_number']}")
print(f"Firmware: {info['rfid_firmware_version']}")
```

**Use Case**: Verify reader identity and firmware version

---

### 1.8 RFM_SET_ALL_PARAM (0x0051) - Set All Parameters
**Status**: ⏳ Not Implemented

**Purpose**: Configure all reader parameters in one command

**Parameters**:
- RF Power
- Antenna selection
- Filter settings
- GPIO configuration
- Network settings
- etc.

**Use Case**: Bulk configuration during setup

---

### 1.9 RFM_GET_ALL_PARAM (0x0052) - Get All Parameters
**Status**: 📝 Helper Available - `build_get_all_params_command()`

**Purpose**: Retrieve all current settings

**Command Format**:
```
HEAD: 0xCF
ADDR: 0xFF
CMD:  0x0052
LEN:  0x00
DATA: (none)
CRC:  2 bytes
```

**Use Case**: Backup current configuration

---

### 1.10 RFM_SET_GET_IOPUT_PARAM (0x0053) - Set/Get I/O Parameters
**Status**: ⏳ Not Implemented

**Purpose**: Configure GPIO input/output behavior

**Use Case**: Configure GPIO pins for external triggers or indicators

---

### 1.11 RFM_SET_GET_WiFi_PARAM (0x0044) - Set/Get WiFi Info
**Status**: ⏳ Not Implemented

**Purpose**: Configure WiFi connection settings

**Use Case**: Connect M-200 to WiFi network

---

### 1.12 RFM_SET_GET_PERMISSION_PARAM (0x0054) - Set/Get Permission
**Status**: ⏳ Not Implemented

**Purpose**: Configure access control and security settings

**Use Case**: Restrict device access

---

### 1.13 RFM_RELEASE_CLOSE_RELAY1 (0x0055) - Control Relay 1
**Status**: ⏳ Not Implemented

**Purpose**: Open/close relay 1 output

**Use Case**: Trigger external devices (doors, gates, alarms)

---

### 1.14 RFM_RELEASE_CLOSE_RELAY2 (0x0056) - Control Relay 2
**Status**: ⏳ Not Implemented

**Purpose**: Open/close relay 2 output

**Use Case**: Control secondary external device

---

### 1.15 RFM_SET_GET_AntN_RSSI_Filter (0x0057) - Set RSSI Filter
**Status**: ⏳ Not Implemented

**Purpose**: Set minimum RSSI threshold for each antenna

**Use Case**: Filter out weak/distant tags

---

## 2️⃣ **ISO 18000-6C Protocol Commands** (Section 2.3)

### 2.1 RFM_INVENTORYISO_CONTINUE (0x0027) - Tag Inventory ⭐
**Status**: ✅ **Implemented** - `read_single_tag()`

**Purpose**: Perform tag inventory (scan for nearby tags)

**Command Format**:
```
HEAD: 0xCF
ADDR: 0xFF
CMD:  0x0027
LEN:  0x02
DATA: [INV_TYPE][INV_PARAM]
      INV_TYPE: 0x00=by time, 0x01=by cycle
      INV_PARAM: seconds or cycle count (0=continuous)
CRC:  2 bytes
```

**Response Format**:
```
STATUS: 0x00 (success) or 0x12 (no tags)
DATA: For each tag found:
  - RSSI (1 byte)
  - Antenna (1 byte)
  - PC (2 bytes)
  - EPC Length (1 byte)
  - EPC Data (variable)
```

**Example**:
```python
# Single read
tags = await rfid_reader_service.read_single_tag()

for tag in tags:
    print(f"EPC: {tag['epc']}")
    print(f"RSSI: {tag['rssi']} dBm")
    print(f"Antenna: {tag['antenna_port']}")
```

**Use Case**: Read tags in range

---

### 2.2 RFM_INVENTORY_STOP (0x0028) - Stop Inventory ⭐
**Status**: ✅ **Implemented** - Called in `stop_scanning()`

**Purpose**: Stop continuous inventory operation

**Command Format**:
```
HEAD: 0xCF
ADDR: 0xFF
CMD:  0x0028
LEN:  0x00
DATA: (none)
CRC:  2 bytes
```

**Example**:
```python
await rfid_reader_service.stop_scanning()
```

**Use Case**: End continuous scanning

---

### 2.3 RFM_READISO_TAG (0x002A) - Read Tag Data
**Status**: 📝 Helper Available - `build_read_tag_command()`

**Purpose**: Read specific memory banks (TID, User memory)

**Command Format**:
```
HEAD: 0xCF
ADDR: 0xFF
CMD:  0x002A
LEN:  0x03
DATA: [MEM_BANK][START_ADDR][WORD_COUNT]
      MEM_BANK: 0=Reserved, 1=EPC, 2=TID, 3=User
      START_ADDR: Starting word address
      WORD_COUNT: Number of 16-bit words to read
CRC:  2 bytes
```

**Example**:
```python
from app.services.m200_protocol import build_read_tag_command

# Read TID (12 bytes = 6 words)
cmd = build_read_tag_command(mem_bank=2, start_addr=0, word_count=6)
response_bytes = await rfid_reader_service._send_command(cmd)
```

**Use Case**: Get unique TID from tag, read user data

---

### 2.4 RFM_SETISO_SELECTMASK (0x002D) - Select Tag to Operate
**Status**: ⏳ Not Implemented

**Purpose**: Target specific tag(s) for subsequent operations

**Use Case**: Write to specific tag when multiple tags present

---

### 2.5 RFM_SET_SELPRM (0x005D) - Set Select Command Parameters
**Status**: ⏳ Not Implemented

**Purpose**: Configure Select command behavior

**Use Case**: Advanced tag filtering

---

### 2.6 RFM_GET_SELPRM (0x005E) - Get Select Command Parameters
**Status**: ⏳ Not Implemented

**Purpose**: Read current Select configuration

**Use Case**: Verify Select settings

---

### 2.7 RFM_SET_QUERY_PARAM (0x005B) - Set Query Parameters
**Status**: ⏳ Not Implemented

**Purpose**: Configure Query command (Q value, session, etc.)

**Use Case**: Optimize for single/multiple tag environments

---

### 2.8 RFM_GET_QUERY_PARAM (0x005C) - Get Query Parameters
**Status**: ⏳ Not Implemented

**Purpose**: Read current Query configuration

**Use Case**: Verify Query settings

---

## 3️⃣ **GPIO Control Commands** (Section 2.4)

### 3.1 RFM_SET_GET_GPIO_WORKPARAM (0x0058) - Set/Get GPIO Parameters
**Status**: ⏳ Not Implemented

**Purpose**: Configure GPIO pin behavior (input/output, pull-up/down, etc.)

**Use Case**: Configure external trigger inputs, status LEDs

---

### 3.2 RFM_GET_GPIO_LEVELS (0x0059) - Get GPIO Levels
**Status**: ⏳ Not Implemented

**Purpose**: Read current GPIO pin states

**Use Case**: Check button/switch states

---

## 4️⃣ **Gate Control Commands** (Section 2.5)

### 4.1 RFM_GET_GATE_STATUS (0x005A) - Get Gate Status
**Status**: ⏳ Not Implemented

**Purpose**: Read gate mode status and tag detection

**Use Case**: Check if person passed through gate

---

### 4.2 RFM_SET_GET_GATE_WORKPARAM (0x005F) - Set/Get Gate Parameters
**Status**: ⏳ Not Implemented

**Purpose**: Configure gate mode behavior (entry/exit detection, EAS alarm, etc.)

**Use Case**: Configure M-200 for gate/portal applications

---

### 4.3 RFM_SET_GET_EAS_MASK (0x0060) - Set/Get EAS Mask
**Status**: ⏳ Not Implemented

**Purpose**: Configure Electronic Article Surveillance (EAS) matching data

**Use Case**: Trigger alarm when specific tags detected

---

## 📊 **Priority for Implementation**

### High Priority (Core Functionality)
1. ✅ `RFM_GET_DEVICE_INFO` (0x0021) - Already done
2. ✅ `RFM_INVENTORYISO_CONTINUE` (0x0027) - Already done
3. ✅ `RFM_INVENTORY_STOP` (0x0028) - Already done
4. 📝 `RFM_SET_PWR` (0x002F) - Helper exists, needs integration
5. 📝 `RFM_READISO_TAG` (0x002A) - Helper exists, needs integration

### Medium Priority (Configuration)
6. `RFM_SET_GET_NETPARA` (0x0042) - Network configuration
7. `RFM_GET_ALL_PARAM` (0x0052) - Read all settings
8. `RFM_SET_ALL_PARAM` (0x0051) - Configure all settings
9. `RFM_SET_GET_AntN_RSSI_Filter` (0x0057) - RSSI filtering

### Low Priority (Advanced Features)
10. `RFM_SET_QUERY_PARAM` (0x005B) - Query optimization
11. `RFM_SETISO_SELECTMASK` (0x002D) - Tag selection
12. `RFM_RELEASE_CLOSE_RELAY1/2` (0x0055/0x0056) - Relay control
13. Gate control commands - For gate/portal applications

---

## 🎯 **Quick Reference: Common Operations**

### Get Device Info
```python
info = await rfid_reader_service.get_reader_info()
```

### Read Tags Once
```python
tags = await rfid_reader_service.read_single_tag()
```

### Continuous Scanning
```python
await rfid_reader_service.start_scanning()
# ... tags are read continuously ...
await rfid_reader_service.stop_scanning()
```

### Set RF Power (using helper)
```python
from app.services.m200_protocol import build_set_power_command

cmd = build_set_power_command(26)  # 26 dBm
response = await rfid_reader_service._send_command(cmd)
```

### Read TID (using helper)
```python
from app.services.m200_protocol import build_read_tag_command

cmd = build_read_tag_command(mem_bank=2, start_addr=0, word_count=6)
response = await rfid_reader_service._send_command(cmd)
```

---

## 📝 **Status Codes Reference** (Appendix C)

| Code | Description |
|------|-------------|
| 0x00 | Success |
| 0x01 | Parameter error |
| 0x02 | Command failed (internal error) |
| 0x03 | Reserved |
| 0x12 | Inventory complete (no tags found) |
| 0x14 | Tag response timeout |
| 0x15 | Tag demodulation error |
| 0x16 | Authentication failed |
| 0x17 | Wrong password |
| 0xFF | No more data |

---

## 🔗 **References**

- **Manual**: `be/CF-M Gate Reader User ManualV1.pdf`
- **Protocol Module**: `be/app/services/m200_protocol.py`
- **Service**: `be/app/services/rfid_reader.py`
- **Section 2.1**: Complete command list (Table A-7)
- **Appendix C**: Status code definitions (Table A-8)

---

**Last Updated**: Based on CF-M Gate Reader User Manual V1.2

**Implementation Status**: 5 of 28 commands (18%) - Core functionality complete, advanced features pending


