import uvicorn
import sys
import os

if __name__ == "__main__":
    # Ensure we are in the 'be' directory context
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    print(f"Python executable: {sys.executable}")

    try:
        import websockets

        print(f"websockets version: {websockets.__version__}")
    except ImportError:
        print("ERROR: websockets module NOT found!")

    try:
        import wsproto

        print(f"wsproto version: {wsproto.__version__}")
    except ImportError:
        print("ERROR: wsproto module NOT found!")

    print("Starting server programmatically...")

    # Run server directly without reload to ensure environment consistency
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, ws="wsproto")
