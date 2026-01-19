import os
import sys

# Add project root to path
sys.path.insert(0, os.getcwd())

print("Attempting to import TagListenerService...")
try:
    from app.services.tag_listener_service import TagListenerService

    print("SUCCESS: TagListenerService imported.")
except ImportError as e:
    print(f"FAILURE: ImportError: {e}")
except Exception as e:
    print(f"FAILURE: Exception: {e}")

print("Attempting to import RFIDReaderService...")
try:
    from app.services.rfid_reader import RFIDReaderService

    print("SUCCESS: RFIDReaderService imported.")
except Exception as e:
    print(f"FAILURE: {e}")
