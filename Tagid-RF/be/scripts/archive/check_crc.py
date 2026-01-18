import struct


def calculate_crc16(data: bytes) -> int:
    PRESET_VALUE = 0xFFFF
    POLYNOMIAL = 0x8408
    crc_value = PRESET_VALUE
    for byte in data:
        crc_value ^= byte
        for _ in range(8):
            if crc_value & 0x0001:
                crc_value = (crc_value >> 1) ^ POLYNOMIAL
            else:
                crc_value = crc_value >> 1
    return crc_value


# Real frame captured from reader (Get Info Response)
# Hex string excluding last 2 bytes (CRC)
hex_frame = "CF010070990043502D3231343931345F56312E313200000000000000000000000000000000005548462047617465205265616465722056312E3120323032352E30342E31302037DD333939390B004B3932344D552D3931345F56312E310000000000000000000000000000000000000000005548462053656E696F72205265616465722056312E352E31322E3133000000002207001E8C12301647343830"
frame_bytes = bytes.fromhex(hex_frame)

# Expected CRC from capture: 8F 3E
expected_crc = 0x8F3E

# Calculate
calc_crc = calculate_crc16(frame_bytes)

print(f"Calculated CRC: 0x{calc_crc:04X}")
print(f"Expected CRC:   0x{expected_crc:04X}")
print(f"Match Big Endian (>H)? {calc_crc == expected_crc}")
print(
    f"Match Little Endian (<H)? {struct.unpack('<H', struct.pack('>H', calc_crc))[0] == expected_crc}"
)
