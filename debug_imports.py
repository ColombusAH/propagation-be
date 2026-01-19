import os
import sys

# Add the backend directory to sys.path
backend_path = os.path.join(os.getcwd(), "Tagid-RF", "be")
sys.path.insert(0, backend_path)

os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/db"
os.environ["SECRET_KEY"] = "test"
os.environ["GOOGLE_CLIENT_ID"] = "test"

try:
    print("Testing import app.core.config...")
    from app.core.config import get_settings

    settings = get_settings()
    print(f"Project Name: {settings.PROJECT_NAME}")

    print("Testing import app.services.database...")
    from app.services.database import engine

    print(f"Engine URL: {engine.url}")

    print("Testing import app.models.rfid_tag...")
    from app.models.rfid_tag import RFIDTag

    print("Success!")
except Exception as e:
    import traceback

    traceback.print_exc()
    sys.exit(1)
