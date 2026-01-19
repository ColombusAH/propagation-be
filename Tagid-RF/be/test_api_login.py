import json

import requests


def test_login():
    url = "http://localhost:8000/api/v1/auth/dev-login"
    payload = {"role": "SUPER_ADMIN"}
    try:
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")


if __name__ == "__main__":
    test_login()
