# Network Setup Guide for RFID Reader

## 🚨 **Current Issue: Different Network Subnets**

**Your Computer**: `10.10.0.50` or `192.168.139.3`  
**RFID Reader**: `192.168.1.200`  
**Problem**: They're on **different networks** and cannot communicate!

---

## ✅ **Solution Options**

### Option 1: Connect Computer to Same Network (RECOMMENDED)

**Connect your computer to the `192.168.1.x` network:**

1. **Via WiFi**:
   - Connect to WiFi network that uses `192.168.1.x` subnet
   - Your computer will get an IP like `192.168.1.xxx`
   - Then you can reach `192.168.1.200`

2. **Via Ethernet**:
   - Connect Ethernet cable to same router/switch as RFID reader
   - Ensure you get an IP in `192.168.1.x` range

3. **Check your connection**:
   ```bash
   # After connecting, check your IP
   ifconfig | grep "inet "
   
   # Should show something like:
   # inet 192.168.1.xxx
   ```

---

### Option 2: Configure Static Route (Advanced)

If you need to stay on your current network but reach the reader:

**macOS**:
```bash
# Add route to 192.168.1.x network
sudo route add -net 192.168.1.0/24 <gateway_ip>

# Example:
sudo route add -net 192.168.1.0/24 10.10.0.1
```

**Linux**:
```bash
sudo ip route add 192.168.1.0/24 via <gateway_ip>
```

**Note**: This requires a router/gateway that can route between subnets.

---

### Option 3: Change RFID Reader IP

If you have access to the reader's settings:

1. **Change reader IP** to match your network:
   - If you're on `10.10.0.x`: Set reader to `10.10.0.200`
   - If you're on `192.168.139.x`: Set reader to `192.168.139.200`

2. **Update subnet mask** to match your network

3. **Set gateway** to your router's IP

---

### Option 4: Use Network Bridge/VPN

If you have network infrastructure:
- Configure router to bridge networks
- Use VPN to connect networks
- Use network switch that spans both subnets

---

## 🔍 **Verify Connection**

Once on the same network, test:

```bash
# 1. Ping the reader
ping 192.168.1.200

# 2. Scan for RFID ports
cd /Users/anverh/projects/propagation-be/be
python3 scan_m200_ports.py --ip 192.168.1.200

# 3. Test RFID connection
python3 debug_m200_connection.py --ip 192.168.1.200 --port 4001
```

---

## 📋 **Quick Checklist**

- [ ] Computer and reader on same network subnet
- [ ] Can ping reader: `ping 192.168.1.200`
- [ ] Port scan finds open ports
- [ ] RFID protocol test succeeds

---

## 💡 **Why This Happens**

**Different subnets cannot communicate directly** without routing:
- `10.10.0.x` network cannot reach `192.168.1.x` directly
- `192.168.139.x` network cannot reach `192.168.1.x` directly
- Need router/gateway to forward packets between subnets

**Link-local addresses** (`169.254.x.x`) are auto-assigned when:
- Device can't get IP from DHCP
- No router on network
- Direct connection between devices

---

## 🎯 **Recommended Action**

**Easiest solution**: Connect your computer to the same network as the RFID reader (`192.168.1.x`).

Then update your `.env`:
```env
RFID_READER_IP=192.168.1.200
RFID_READER_PORT=4001
```

And test:
```bash
python3 debug_m200_connection.py --ip 192.168.1.200 --port 4001
```

---

**Once on the same network, the RFID reader should be reachable!**


