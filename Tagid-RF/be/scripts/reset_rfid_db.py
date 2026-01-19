import os
import sys

# Add parent directory to path to allow importing app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.rfid_tag import RFIDScanHistory, RFIDTag
from app.services.database import Base, engine


def reset_db():
    print("Resetting RFID Database Tables...")
    try:
        # Drop specific tables
        RFIDTag.__table__.drop(engine, checkfirst=True)
        print("Dropped rfid_tags table.")

        # We also need to drop history if it depends on tag or if we want clean slate
        # RFIDScanHistory.__table__.drop(engine, checkfirst=True)
        # print("Dropped rfid_scan_history table.")

        # Re-create all tables (this will only create missing ones, so it recreates what we dropped)
        Base.metadata.create_all(bind=engine)
        print("Re-created tables with updated schema.")

    except Exception as e:
        print(f"Error resetting DB: {e}")


if __name__ == "__main__":
    reset_db()
