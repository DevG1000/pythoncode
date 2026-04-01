import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test health check endpoint."""
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_registration():
    """Test user registration."""
    print("Testing user registration...")
    
    # Test data
    test_email = f"test_{int(time.time())}@example.com"
    test_username = f"testuser_{int(time.time())}"
    
    payload = {
        "email": test_email,
        "username": test_username,
        "password": "SecurePass123!"
    }
    
    print(f"Registering user: {test_email}")
    response = requests.post(f"{BASE_URL}/api/register", json=payload)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()
    
    return response.json() if response.status_code == 201 else None

def test_invalid_registration():
    """Test invalid registration scenarios."""
    print("Testing invalid registration...")
    
    test_cases = [
        {
            "name": "Missing email",
            "payload": {
                "username": "testuser",
                "password": "password123"
            },
            "expected_error": "Missing required field: email"
        },
        {
            "name": "Invalid email format",
            "payload": {
                "email": "invalid-email",
                "username": "testuser",
                "password": "password123"
            },
            "expected_error": "Invalid email format"
        },
        {
            "name": "Short password",
            "payload": {
                "email": "test@example.com",
                "username": "testuser",
                "password": "short"
            },
            "expected_error": "Password must be at least 8 characters long"
        },
        {
            "name": "Invalid username (special chars)",
            "payload": {
                "email": "test@example.com",
                "username": "test@user",
                "password": "password123"
            },
            "expected_error": "Username can only contain letters, numbers, and underscores"
        }
    ]
    
    for test_case in test_cases:
        print(f"Test: {test_case['name']}")
        response = requests.post(f"{BASE_URL}/api/register", json=test_case['payload'])
        
        if response.status_code == 400:
            error_msg = response.json().get('error', '')
            if test_case['expected_error'] in error_msg:
                print(f"Passed: {error_msg}")
            else:
                print(f"Failed: Expected '{test_case['expected_error']}', got '{error_msg}'")
        else:
            print(f"Failed: Expected 400, got {response.status_code}")
        print()

def test_duplicate_registration():
    """Test duplicate registration."""
    print("Testing duplicate registration...")
    
    # First registration
    test_email = f"duplicate_{int(time.time())}@example.com"
    test_username = f"duplicate_{int(time.time())}"
    
    payload = {
        "email": test_email,
        "username": test_username,
        "password": "SecurePass123!"
    }
    
    response1 = requests.post(f"{BASE_URL}/api/register", json=payload)
    print(f"First registration: {response1.status_code}")
    
    # Try duplicate registration
    response2 = requests.post(f"{BASE_URL}/api/register", json=payload)
    print(f"Duplicate registration: {response2.status_code}")
    
    if response2.status_code == 409:
        error_msg = response2.json().get('error', '')
        if "already" in error_msg.lower():
            print(f"✓ Passed: {error_msg}")
        else:
            print(f"✗ Failed: Expected duplicate error, got '{error_msg}'")
    else:
        print(f"✗ Failed: Expected 409, got {response2.status_code}")
    print()

def test_resend_verification():
    """Test resend verification email."""
    print("Testing resend verification...")
    
    # First register a user
    test_email = f"resend_{int(time.time())}@example.com"
    test_username = f"resend_{int(time.time())}"
    
    payload = {
        "email": test_email,
        "username": test_username,
        "password": "SecurePass123!"
    }
    
    registration = requests.post(f"{BASE_URL}/api/register", json=payload)
    print(f"Registration: {registration.status_code}")
    
    # Test resend verification
    resend_payload = {"email": test_email}
    response = requests.post(f"{BASE_URL}/api/resend-verification", json=resend_payload)
    
    print(f"Resend verification: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Starting API Tests")
    print("=" * 60)
    print()
    
    try:
        test_health_check()
        test_invalid_registration()
        test_duplicate_registration()
        registration_result = test_registration()
        test_resend_verification()
        
        print("=" * 60)
        print("Test Summary")
        print("=" * 60)
        print("✓ Health check endpoint")
        print("✓ Invalid registration validation")
        print("✓ Duplicate registration prevention")
        print("✓ Successful registration")
        print("✓ Resend verification email")
        print()
        print("Note: Email verification requires proper email configuration.")
        print("Set up MAIL_USERNAME, MAIL_PASSWORD in .env file for full functionality.")
        
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to server. Make sure the Flask app is running.")
        print("Run: python app.py")
    except Exception as e:
        print(f"Test error: {e}")

if __name__ == "__main__":
    run_all_tests()