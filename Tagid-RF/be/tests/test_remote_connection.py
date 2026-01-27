import requests
import time
import sys

def test_url(name, url, headers=None):
    print(f"Testing {name}: {url}...")
    try:
        start_time = time.time()
        # Adding localtunnel bypass header
        if headers is None:
            headers = {}
        headers['bypass-tunnel-reminder'] = 'true'
        
        response = requests.get(url, headers=headers, timeout=10)
        elapsed = time.time() - start_time
        print(f"  Status: {response.status_code}")
        print(f"  Time: {elapsed:.2f}s")
        if response.status_code == 200:
            print(f"  Result: SUCCESS")
        elif response.status_code == 404:
            print(f"  Result: NOT FOUND (but connection worked)")
        else:
            print(f"  Result: FAILED ({response.reason})")
    except Exception as e:
        print(f"  Error: {str(e)}")
    print("-" * 40)

def main():
    # Local checks
    test_url("Local Web", "http://localhost:5173")
    test_url("Local API", "http://localhost:8000/api/v1/health")
    
    # Remote checks (from previous attempt)
    test_url("Remote Web", "https://unique-tagid-web-998877.loca.lt")
    test_url("Remote API", "https://eliran-tagid-api-final.loca.lt")

if __name__ == "__main__":
    main()
