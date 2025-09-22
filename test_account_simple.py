import requests
import sys

def test_account_creation():
    session = requests.Session()
    
    # Login as admin
    print("Logging in as admin...")
    login = session.post('http://localhost:5000/admin_login', data={
        'username': 'admin', 
        'password': 'a123'
    })
    print(f"Login status: {login.status_code}")
    
    if login.status_code != 200:
        print("Admin login failed!")
        return False
    
    # Create account with unique data
    print("Creating account...")
    create_data = {
        'name': 'Jane Smith',
        'mobile': '9999999999',
        'email': 'janesmith@example.com',
        'address': '789 Unique Street',
        'dob': '1992-03-20',
        'aadhar': '333333333333',
        'preferred_currency': 'INR',
        'pin': '9999'
    }
    
    print(f"Sending data: {create_data}")
    create = session.post('http://localhost:5000/enhanced_create_account', data=create_data)
    
    print(f"Create status: {create.status_code}")
    print(f"Response length: {len(create.text)}")
    
    if 'successfully' in create.text:
        print("✅ SUCCESS: Account created!")
        # Extract account number
        import re
        account_match = re.search(r'Account Number: (\d+)', create.text)
        if account_match:
            print(f"Account Number: {account_match.group(1)}")
        return True
    else:
        print("❌ FAILED: Account not created")
        print("Response preview:")
        print(create.text[:500])
        
        # Save full response for debugging
        with open('failed_response.html', 'w') as f:
            f.write(create.text)
        print("Full response saved to failed_response.html")
        return False

if __name__ == "__main__":
    success = test_account_creation()
    sys.exit(0 if success else 1)