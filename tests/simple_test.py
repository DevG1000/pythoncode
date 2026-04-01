import requests
import json
import time

BASE_URL = "http://localhost:5000"

def simple_test():
    """简单API测试"""
    print("=" * 50)
    print("Simple API Test")
    print("=" * 50)
    
    try:
        # Test health check
        print("\n1. Testing health check...")
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test registration
        print("\n2. Testing user registration...")
        timestamp = int(time.time())
        payload = {
            "email": f"test_{timestamp}@example.com",
            "username": f"testuser_{timestamp}",
            "password": "SecurePass123!"
        }
        
        response = requests.post(f"{BASE_URL}/api/register", json=payload, timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"   Message: {data.get('message', 'N/A')}")
            print(f"   User ID: {data.get('user', {}).get('id', 'N/A')}")
            print(f"   Email sent: {data.get('email_sent', 'N/A')}")
            
            # Check database file
            import os
            if os.path.exists("users.db"):
                print(f"   Database created: users.db ({os.path.getsize('users.db')} bytes)")
            else:
                print("   Database file not found")
        else:
            print(f"   Error: {response.json().get('error', 'N/A')}")
        
        print("\n" + "=" * 50)
        print("Test completed!")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot connect to server")
        print("Make sure the API server is running:")
        print("   python app.py")
    except Exception as e:
        print(f"\n[ERROR] Test error: {e}")

if __name__ == "__main__":
    simple_test()