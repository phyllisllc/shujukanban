import urllib.request
try:
    with urllib.request.urlopen('http://localhost:5001/') as response:
        print(f"Status: {response.getcode()}")
except Exception as e:
    print(f"Error: {e}")
