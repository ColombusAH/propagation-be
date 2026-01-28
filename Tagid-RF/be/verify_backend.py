import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def check_backend_health():
    try:
        response = requests.get("http://localhost:8000/healthz")
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend returned {response.status_code}")
            return False
    except:
        print("❌ Could not connect to backend")
        return False

def check_vapid():
    url = f"{BASE_URL}/push/vapid-public-key"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "publicKey" in data:
                print(f"✅ VAPID Public Key endpoint working!")
                print(f"   Key length: {len(data['publicKey'])}")
                return True
            else:
                print("❌ VAPID response missing publicKey")
        elif response.status_code == 404:
            print(f"❌ Endpoint not found (404): {url}")
            print("   (Router not mounted or incorrect prefix)")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error checking VAPID: {e}")
    return False

if __name__ == "__main__":
    print("--- Web Push Verification ---")
    if check_backend_health():
        check_vapid()
    print("-----------------------------")
