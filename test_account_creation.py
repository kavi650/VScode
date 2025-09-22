import requests
import json

# Test account creation
url = "http://localhost:5000/enhanced_create_account"
data = {
    'name': 'Test User',
    'mobile': '9876543210',
    'email': 'test@example.com',
    'address': '123 Test Street',
    'date_of_birth': '1990-01-01',
    'aadhar': '123456789012',
    'preferred_currency': 'INR',
    'pin': '1234'
}

print("Testing account creation with data:")
print(json.dumps(data, indent=2))

try:
    response = requests.post(url, data=data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")