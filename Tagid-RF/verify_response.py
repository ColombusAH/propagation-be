import urllib.request
import urllib.error

url = "https://web-production-3882f.up.railway.app/api/v1/auth/dev-login"
print(f"Testing URL: {url}")

try:
    req = urllib.request.Request(url, method="POST")
    with urllib.request.urlopen(req) as response:
        print(f"Status: {response.status}")
        print("Headers:")
        for k, v in response.headers.items():
            print(f"  {k}: {v}")
        print("\nBody:")
        print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} {e.reason}")
    print("Headers:")
    for k, v in e.headers.items():
        print(f"  {k}: {v}")
    print("\nBody:")
    print(e.read().decode('utf-8'))
except Exception as e:
    print(f"Error: {e}")
