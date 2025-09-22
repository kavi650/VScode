import requests

# Test admin login first
login_url = "http://localhost:5000/admin_login"
login_data = {
    'username': 'admin',
    'password': 'a123'
}

session = requests.Session()

print("Step 1: Logging in as admin...")
try:
    response = session.post(login_url, data=login_data)
    print(f"Login Status Code: {response.status_code}")
    print(f"Login Response URL: {response.url}")
    
    # Check if we got redirected to admin dashboard
    if 'admin_dashboard' in response.url:
        print("✅ Admin login successful!")
        
        # Now try to access account creation page
        print("\nStep 2: Accessing account creation page...")
        account_url = "http://localhost:5000/enhanced_create_account"
        account_response = session.get(account_url)
        print(f"Account Creation Page Status: {account_response.status_code}")
        
        if account_response.status_code == 200:
            print("✅ Account creation page accessible!")
            
            # Test actual account creation
            print("\nStep 3: Testing account creation...")
            account_data = {
                'name': 'Test User',
                'mobile': '9876543210',
                'email': 'test@example.com',
                'address': '123 Test Street',
                'dob': '1990-01-01',
                'aadhar': '123456789012',
                'preferred_currency': 'INR',
                'pin': '1234'
            }
            
            create_response = session.post(account_url, data=account_data)
            print(f"Account Creation Status: {create_response.status_code}")
            print(f"Account Creation Response Length: {len(create_response.text)} characters")
            
            if 'Account created successfully' in create_response.text:
                print("✅ Account created successfully!")
            else:
                print("❌ Account creation may have failed")
                print("Response preview:", create_response.text[:200])
        else:
            print("❌ Account creation page not accessible")
    else:
        print("❌ Admin login failed")
        print("Response preview:", response.text[:200])
        
except Exception as e:
    print(f"Error: {e}")