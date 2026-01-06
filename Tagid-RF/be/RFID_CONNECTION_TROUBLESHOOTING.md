# RFID Reader Connection Troubleshooting Guide

## 🚨 **Current Status: Cannot Find RFID Reader**

We've scanned your network and cannot find a Chafon RFID reader responding to the protocol.

---

## 📋 **Step-by-Step Troubleshooting**

### Step 1: Find the RFID Reader's IP Address

The RFID reader MUST be assigned an IP address. Here's how to find it:

#### Option A: Check the Reader Display (if it has one)
1. Power on the RFID reader
2. Navigate to network settings menu
3. Look for "IP Address" or "Network Info"
4. Write down the IP address shown

#### Option B: Check Your Router
1. Log into your router admin panel (usually `192.168.1.1` or `192.168.0.1`)
2. Look for "Connected Devices" or "DHCP Client List"
3. Find device with name like "Chafon", "RFID", "CF-M", "UHF Reader"
4. Note its IP address

#### Option C: Use Network Scanner
```bash
# macOS
arp -a | grep -i "169.254"

# Find all link-local devices
```

---

### Step 2: Verify Physical Connection

#### If Connected via Ethernet:
- ✅ Check cable is securely plugged in
- ✅ Check link lights are on (both on reader and computer/router)
- ✅ Verify reader is powered on
- ✅ Make sure you're on the same network

#### If Using WiFi:
- ✅ Check reader is connected to your WiFi network
- ✅ Verify WiFi settings in reader menu
- ✅ Ensure no MAC address filtering on router

---

### Step 3: Check Reader Configuration

Your reader might be in **configuration mode** instead of **TCP server mode**.

According to the CF READER.DLL guide, the reader needs to be configured to enable TCP communication.

**Common issues**:
1. **TCP Server not enabled** - Check reader settings
2. **Wrong port number** - Default should be 4001, but could be different
3. **Firewall on reader** - Might be blocking connections
4. **Wrong network mode** - Reader might be in USB-only mode

---

### Step 4: Test Basic Connectivity

Once you have the correct IP address:

```bash
# Test ping
ping <READER_IP>

# Test if any ports are open
nc -zv <READER_IP> 4001
nc -zv <READER_IP> 5000
nc -zv <READER_IP> 6000
nc -zv <READER_IP> 8080
```

---

### Step 5: Try Different Network Subnets

Your reader might be on a different subnet. Try scanning:

```bash
# Scan different subnets
python3 find_rfid_reader.py --subnet 192.168.1
python3 find_rfid_reader.py --subnet 192.168.0
python3 find_rfid_reader.py --subnet 169.254.128
python3 find_rfid_reader.py --subnet 10.0.0
```

---

## 🔧 **Reader Configuration Checklist**

Based on the **CF READER.DLL User Guide** and **M-Series Manual**, verify these settings:

### Network Settings (Section 2.2.5 of manual)
- [ ] **IP Address** - Static IP assigned (e.g., 192.168.1.100)
- [ ] **Subnet Mask** - Matches your network (usually 255.255.255.0)
- [ ] **Gateway** - Your router IP (e.g., 192.168.1.1)
- [ ] **TCP Server** - Enabled
- [ ] **TCP Port** - Usually 4001 or 5000

### Reader Mode
- [ ] **Operating Mode** - Should be "TCP Server" or "Network Mode"
- [ ] **Not** in "USB Mode" or "Configuration Mode"

---

## 🎯 **What We Discovered So Far**

### IP: 169.254.128.161 (Previous attempt)
- Port 5000: ✅ Open, ❌ No RFID response
- Port 9090: ✅ Open, ⚠️ HTTP interface (not standard RFID protocol)
- Result: **Not the RFID reader's data port**

### IP: 169.254.173.142 (Second attempt)
- Port 5000: ✅ Open, ❌ Responds as "AirTunes" (Apple device)
- Result: **Wrong device - This is a Mac/iPhone/AppleTV**

### Network Scan: 169.254.173.x
- Scanned 254 IPs × 6 ports = 1524 endpoints
- Result: ❌ **No RFID readers found**

---

## 💡 **Likely Issues**

1. **Wrong IP Address**
   - The IPs you provided (169.254.x.x) are **link-local** addresses
   - These are assigned when DHCP fails
   - Reader might have different IP

2. **Reader Not on Network**
   - Reader might be connected via USB only
   - Reader might be powered off
   - Wrong network interface

3. **TCP Server Disabled**
   - Reader might not have TCP server enabled
   - Might be in configuration/setup mode
   - Might require special activation

4. **Different Protocol**
   - Your specific model might use HTTP REST API
   - Might need Windows DLL (from CF READER.DLL guide)
   - Might use proprietary software

---

## 🛠️ **Recommended Actions**

### Immediate Actions:
1. **Find the actual IP address** from reader display or router
2. **Check reader documentation** for your specific model
3. **Verify TCP server is enabled** in reader settings
4. **Try connecting via USB** first (if available)

### Using the DLL Guide:
The **CF READER.DLL User Guide V1.1** suggests the reader is designed to work with Windows software. This might mean:
- Reader expects Windows DLL integration
- Might have web interface for configuration
- TCP protocol might need special initialization

### Test with Manufacturer Software:
1. Try official Chafon software (if available)
2. Use it to:
   - Verify reader works
   - Check current IP address
   - Enable TCP server mode
   - Get firmware version

---

## 📞 **Need More Information**

Please provide:

1. **Exact model number** of your RFID reader (e.g., CF-M200, CF-001-548)
2. **How is it connected?**
   - Ethernet cable to router?
   - Direct to computer?
   - WiFi?
   - USB?

3. **Does it have a display?**
   - Can you see IP address on screen?
   - What does the display show?

4. **What software came with it?**
   - Do you have Windows configuration software?
   - Any mobile apps?

5. **Documentation**
   - Do you have other manuals?
   - Quick start guide?

---

## 🔍 **Alternative: Direct USB Connection**

If network connection isn't working, try USB connection:

1. **Connect via USB cable**
2. **Find serial port**:
   ```bash
   # macOS
   ls /dev/tty.*
   
   # Linux
   ls /dev/ttyUSB* /dev/ttyACM*
   
   # Windows
   # Check Device Manager → Ports (COM & LPT)
   ```

3. **Test serial connection**:
   ```bash
   # Use pyserial
   python3 -c "import serial; print(serial.tools.list_ports.comports())"
   ```

---

## 📝 **Summary**

**Problem**: Cannot find RFID reader on network  
**Root Cause**: Unknown - Reader might be:
- On different IP/subnet
- Not configured for TCP
- Using different protocol
- Not connected to network

**Next Step**: **Find the reader's actual IP address** from device display or router admin panel

Once you have the correct IP, run:
```bash
python3 debug_m200_connection.py --ip <ACTUAL_IP> --port 4001
```

---

**Need help?** Provide the information requested above and we'll figure it out!


