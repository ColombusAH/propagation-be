# Direct USB-to-Ethernet Connection Setup

## 📋 **Current Situation**

You have a **direct USB-to-Ethernet connection** to the RFID reader:
- **Your Computer**: `169.254.203.81` (self-assigned)
- **Status**: "Self-assigned IP" (no router/DHCP)
- **Connection**: USB 10/100/1000 LAN adapter

This is a **direct point-to-point connection** - perfect for RFID reader communication!

---

## ✅ **Solution: Configure Static IPs**

Since there's no router, we need to set **static IPs** on both devices.

### Step 1: Configure Your Computer's IP

**macOS Network Settings:**

1. **Open System Settings** → **Network**
2. **Select "USB 10/100/1000 LAN"**
3. **Click "Details..."**
4. **Go to "TCP/IP" tab**
5. **Configure IPv4:**
   - **Configure IPv4**: Select "Manually"
   - **IP Address**: `192.168.1.100`
   - **Subnet Mask**: `255.255.255.0`
   - **Router**: Leave empty (no router in direct connection)
6. **Click "Apply"**

**OR via Terminal:**
```bash
# Set static IP on USB Ethernet interface
# First, find the interface name:
ifconfig | grep -A 5 "USB"

# Then set static IP (replace 'enX' with your interface):
sudo ifconfig enX 192.168.1.100 netmask 255.255.255.0
```

---

### Step 2: Configure RFID Reader's IP

The reader needs to be configured to use a static IP in the same subnet.

**Option A: Via Reader Display (if available)**
1. Navigate to Network Settings
2. Set **IP Address**: `192.168.1.200`
3. Set **Subnet Mask**: `255.255.255.0`
4. Set **Gateway**: Leave empty or `0.0.0.0`
5. **Enable TCP Server** (important!)
6. Set **TCP Port**: `4001` (or check manual)

**Option B: Via Web Interface (if available)**
1. Try accessing: `http://169.254.203.1` or `http://169.254.203.100`
2. Look for network configuration page
3. Set static IP: `192.168.1.200`

**Option C: Via Configuration Software**
- Use manufacturer's configuration tool
- Connect via USB or initial network setup
- Configure network settings

---

### Step 3: Verify Connection

After configuring both devices:

```bash
# 1. Ping the reader
ping 192.168.1.200

# 2. Test RFID protocol
cd /Users/anverh/projects/propagation-be/be
python3 debug_m200_connection.py --ip 192.168.1.200 --port 4001
```

---

## 🔍 **Alternative: Find Reader's Current IP**

If the reader already has an IP assigned, try to discover it:

### Method 1: Check ARP Table
```bash
# After connecting, check ARP cache
arp -a | grep -i "169.254"

# Or flush and check again
sudo arp -a -d
# Wait a few seconds, then:
arp -a
```

### Method 2: Try Common Link-Local IPs
```bash
# Try common self-assigned IPs
for ip in 169.254.203.1 169.254.203.100 169.254.1.1 169.254.1.100; do
    echo "Testing $ip..."
    ping -c 1 -W 1 $ip 2>&1 | grep "1 packets received" && echo "✓ $ip is reachable"
done
```

### Method 3: Network Scan
```bash
# Scan the link-local range
cd /Users/anverh/projects/propagation-be/be
python3 find_rfid_reader.py --subnet 169.254.203
```

---

## ⚙️ **Reader Configuration Checklist**

Based on the **CF READER.DLL User Guide** and **M-Series Manual**, ensure:

- [ ] **TCP Server Enabled** - Critical! Reader must be in TCP server mode
- [ ] **Static IP Configured** - Same subnet as your computer
- [ ] **Port Number** - Usually 4001 (check manual for your model)
- [ ] **Not in USB Mode** - Should be in Network/TCP mode
- [ ] **Firmware Updated** - Latest firmware might have better network support

---

## 🎯 **Quick Test After Configuration**

Once both devices have static IPs:

```bash
# Update .env
echo "RFID_READER_IP=192.168.1.200" >> .env
echo "RFID_READER_PORT=4001" >> .env

# Test connection
cd /Users/anverh/projects/propagation-be/be
python3 debug_m200_connection.py --ip 192.168.1.200 --port 4001
```

---

## 💡 **Why Direct Connection is Good**

**Advantages:**
- ✅ No network interference
- ✅ Direct, fast communication
- ✅ No router configuration needed
- ✅ Isolated from other network traffic

**Requirements:**
- ✅ Both devices need static IPs
- ✅ Same subnet (e.g., both `192.168.1.x`)
- ✅ TCP server must be enabled on reader

---

## 🚨 **Troubleshooting**

### Issue: Still can't connect after setting static IPs

**Check:**
1. **Reader TCP Server** - Is it enabled?
2. **Port Number** - Try different ports (4001, 5000, 6000)
3. **Firewall** - Disable firewall temporarily to test
4. **Cable** - Try different USB-to-Ethernet adapter
5. **Reader Power** - Ensure reader is fully powered on

### Issue: Reader doesn't have display/settings

**Try:**
1. **Web Interface** - Access via browser at reader's IP
2. **Configuration Software** - Use manufacturer's tool
3. **Serial/USB** - Connect via serial port for initial setup
4. **Default IP** - Check manual for factory default IP

---

## 📝 **Next Steps**

1. **Set your computer's static IP** to `192.168.1.100`
2. **Configure reader's static IP** to `192.168.1.200`
3. **Enable TCP server** on reader
4. **Test connection** with debug script

Once configured, the direct connection should work perfectly!

---

**Current Status**: Direct USB-to-Ethernet connection detected, but reader IP/configuration unknown.  
**Action Required**: Configure static IPs on both devices and enable TCP server on reader.


