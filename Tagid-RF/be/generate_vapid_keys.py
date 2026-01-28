import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

def generate_vapid_keys():
    # Generate private key
    private_key = ec.generate_private_key(ec.SECP256R1())
    
    # Get private key bytes (32 bytes raw)
    private_value = private_key.private_numbers().private_value
    private_bytes = private_value.to_bytes(32, byteorder='big')
    private_b64 = base64.urlsafe_b64encode(private_bytes).decode('utf-8').rstrip('=')
    
    # Get public key bytes (65 bytes uncompressed: 0x04 + x + y)
    public_key = private_key.public_key()
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )
    public_b64 = base64.urlsafe_b64encode(public_bytes).decode('utf-8').rstrip('=')
    
    print("VAPID Keys Generated Successfully!")
    print("-" * 30)
    print(f"VAPID_PRIVATE_KEY={private_b64}")
    print(f"VAPID_PUBLIC_KEY={public_b64}")
    print(f"VAPID_CLAIMS_SUB=mailto:admin@example.com")
    print("-" * 30)

if __name__ == "__main__":
    generate_vapid_keys()
