import requests
import json

url = "http://localhost:8000/api/v1/push/send-notification"
payload = {
    "title": "Hello",
    "body": "This is a test notification",
    "icon": "/vite.svg"
}
headers = {"Content-Type": "application/json"}

print(f"Sending request to {url}...")
try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
