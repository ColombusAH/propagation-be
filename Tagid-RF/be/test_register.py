
import requests
import json

payload = {
    "email": "eliran8hadad@gmail.com",
    "password": "Password123!",
    "name": "Eliran Hadad",
    "phone": "0545486607",
    "address": "Test Address",
    "businessId": ""
}

try:
    print("Attempting registration...")
    response = requests.post("http://127.0.0.1:8000/api/v1/auth/register", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
