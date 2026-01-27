import requests

def test_products_api():
    urls = [
        'http://127.0.0.1:8000/api/v1/products/',
        'http://localhost:8000/api/v1/products/'
    ]
    for url in urls:
        print(f"\nTesting URL: {url}")
        try:
            response = requests.get(url, timeout=5)
            print(f"Status Code: {response.status_code}")
            try:
                print(f"Response: {response.json()}")
            except:
                print(f"Raw Response: {response.text}")
        except Exception as e:
            print(f"Error connecting to {url}: {e}")

if __name__ == "__main__":
    test_products_api()
