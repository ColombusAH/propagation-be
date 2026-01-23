"""
=============================================================================
Chafon M-200 Reader - Using Official DLL (UHFPrimeReader.dll)
=============================================================================
This script uses the manufacturer's DLL via ctypes instead of raw protocol.
The DLL handles all protocol complexities internally.
=============================================================================
"""

import ctypes
import os
import sys
from ctypes import POINTER, Structure, byref, c_byte, c_char_p, c_int, c_uint, c_ushort, c_void_p

# DLL path
DLL_PATH = r"c:\Users\eliran_ha\Documents\Eliran\propagation-be\Tagid-RF\be\Files\Chaphon\M100.200.300.400+SDK\M100.200.300.400 SDK\Library\Win\x64\UHFPrimeReader.dll"


# Structures matching the C# definitions
class DeviceParam(Structure):
    _fields_ = [
        ("cp_hw_ver", c_byte * 32),
        ("cp_fw_ver", c_byte * 32),
        ("cp_sn", c_byte * 12),
        ("rfid_hw_ver", c_byte * 32),
        ("rfid_name", c_byte * 32),
        ("rfid_sn", c_byte * 12),
    ]


class GateGPIOParam(Structure):
    _fields_ = [
        ("work_mode", c_byte),
        ("trigger_mode", c_byte),
        ("relay_time", c_ushort),
        ("beep_time", c_ushort),
        ("reserved", c_byte * 10),
    ]


class AccessOperateParam(Structure):
    _fields_ = [
        ("access_mode", c_byte),
        ("wiegand_bits", c_byte),
        ("epc_start", c_byte),
        ("epc_length", c_byte),
        ("reserved", c_byte * 12),
    ]


def bytes_to_str(byte_array):
    """Convert ctypes byte array to string."""
    result = bytes(byte_array).rstrip(b"\x00").decode("ascii", errors="ignore")
    return result


def main():
    ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.1.200"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 2022

    print("=" * 60)
    print("Chafon M-200 Reader - Using Official DLL")
    print("=" * 60)
    print(f"DLL: {DLL_PATH}")
    print(f"Target: {ip}:{port}")
    print()

    # Check DLL exists
    if not os.path.exists(DLL_PATH):
        print(f"[FAIL] DLL not found: {DLL_PATH}")
        return 1

    # Load DLL
    print("Loading DLL...")
    try:
        dll = ctypes.CDLL(DLL_PATH)
        print("[OK] DLL loaded successfully")
    except Exception as e:
        print(f"[FAIL] Failed to load DLL: {e}")
        return 1

    # Define function signatures
    print("Setting up function signatures...")

    # int OpenNetConnection(out IntPtr handler, string ip, ushort port, uint timeoutMs)
    dll.OpenNetConnection.argtypes = [POINTER(c_void_p), c_char_p, c_ushort, c_uint]
    dll.OpenNetConnection.restype = c_int

    # int CloseDevice(IntPtr hComm)
    dll.CloseDevice.argtypes = [c_void_p]
    dll.CloseDevice.restype = c_int

    # int GetDevicePara(IntPtr hComm, out DeviceParam devInfo)
    dll.GetDevicePara.argtypes = [c_void_p, POINTER(DeviceParam)]
    dll.GetDevicePara.restype = c_int

    # int GetGPIOWorkParam(IntPtr handler, out GateGPIOParam gpioInfo)
    dll.GetGPIOWorkParam.argtypes = [c_void_p, POINTER(GateGPIOParam)]
    dll.GetGPIOWorkParam.restype = c_int

    # int GetAccessOperateParam(IntPtr handler, out AccessOperateParam aParam)
    dll.GetAccessOperateParam.argtypes = [c_void_p, POINTER(AccessOperateParam)]
    dll.GetAccessOperateParam.restype = c_int

    print("[OK] Function signatures set")
    print()

    # Connect
    print("-" * 60)
    print("STEP 1: Connect to Reader")
    print("-" * 60)

    handler = c_void_p()
    ip_bytes = ip.encode("ascii")
    timeout_ms = 5000

    print(f"  Connecting to {ip}:{port} (timeout: {timeout_ms}ms)...")
    result = dll.OpenNetConnection(byref(handler), ip_bytes, port, timeout_ms)

    if result == 0:
        print(f"  [OK] Connected! Handler: {handler.value}")
    else:
        print(f"  [FAIL] Connection failed. Error code: {result}")
        return 1

    print()

    # Get Device Info
    print("-" * 60)
    print("STEP 2: Get Device Parameters")
    print("-" * 60)

    dev_param = DeviceParam()
    result = dll.GetDevicePara(handler, byref(dev_param))

    if result == 0:
        print("  [OK] Device parameters retrieved:")
        print(f"    CP Hardware: {bytes_to_str(dev_param.cp_hw_ver)}")
        print(f"    CP Firmware: {bytes_to_str(dev_param.cp_fw_ver)}")
        print(f"    CP Serial:   {bytes_to_str(dev_param.cp_sn)}")
        print(f"    RFID HW:     {bytes_to_str(dev_param.rfid_hw_ver)}")
        print(f"    RFID Name:   {bytes_to_str(dev_param.rfid_name)}")
        print(f"    RFID Serial: {bytes_to_str(dev_param.rfid_sn)}")
    else:
        print(f"  [FAIL] Error code: {result}")

    print()

    # Get GPIO Params
    print("-" * 60)
    print("STEP 3: Get GPIO Work Parameters")
    print("-" * 60)

    gpio_param = GateGPIOParam()
    result = dll.GetGPIOWorkParam(handler, byref(gpio_param))

    if result == 0:
        print("  [OK] GPIO parameters retrieved:")
        print(f"    Work Mode:    {gpio_param.work_mode}")
        print(f"    Trigger Mode: {gpio_param.trigger_mode}")
        print(f"    Relay Time:   {gpio_param.relay_time}ms")
        print(f"    Beep Time:    {gpio_param.beep_time}ms")
    else:
        print(f"  [FAIL] Error code: {result}")

    print()

    # Get Access Parameters
    print("-" * 60)
    print("STEP 4: Get Access Operate Parameters")
    print("-" * 60)

    access_param = AccessOperateParam()
    result = dll.GetAccessOperateParam(handler, byref(access_param))

    if result == 0:
        print("  [OK] Access parameters retrieved:")
        print(f"    Access Mode:   {access_param.access_mode}")
        print(f"    Wiegand Bits:  {access_param.wiegand_bits}")
        print(f"    EPC Start:     {access_param.epc_start}")
        print(f"    EPC Length:    {access_param.epc_length}")
    else:
        print(f"  [FAIL] Error code: {result}")

    print()

    # Close connection
    print("-" * 60)
    print("STEP 5: Disconnect")
    print("-" * 60)

    result = dll.CloseDevice(handler)
    if result == 0:
        print("  [OK] Disconnected successfully")
    else:
        print(f"  [WARN] Disconnect returned: {result}")

    print()
    print("=" * 60)
    print("DONE")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
