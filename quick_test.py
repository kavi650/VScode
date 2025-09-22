#!/usr/bin/env python3
"""
Quick test to verify account creation is working.
"""

import requests
import time
import random

def test_account_creation():
    """Test account creation with unique data"""
    
    # Generate unique test data
    timestamp = str(int(time.time()))[-4:]
    mobile = f"9{timestamp}{random.randint(1000, 9999)}"
    aadhar = f"{timestamp}{random.randint(100000, 999999)}"
    email = f"test{timestamp}@example.com"
    
    print("🧪 Testing Account Creation")
    print("=" * 30)
    
    # Create session
    session = requests.Session()
    
    # Login as admin
    print("1. Logging in as admin...")
    login = session.post('http://localhost:5000/admin_login', data={
        'username': 'admin',
        'password': 'a123'
    })
    
    if login.status_code == 200:
        print("   ✅ Admin login successful")
        
        # Create account
        print("\n2. Creating account...")
        account_data = {
            'name': f'Test User {timestamp}',
            'email': email,
            'mobile': mobile,
            'address': '123 Test Street',
            'dob': '1990-01-01',
            'aadhar': aadhar,
            'pin': '1234',
            'preferred_currency': 'INR'
        }
        
        create = session.post('http://localhost:5000/enhanced_create_account', data=account_data)
        print(f"   Status: {create.status_code}")
        
        if create.status_code == 200:
            # Check response
            if 'Account Created Successfully' in create.text:
                print("   ✅ Account created successfully!")
                
                # Extract details
                import re
                account_match = re.search(r'Account Number:</strong> (\d+)', create.text)
                pin_match = re.search(r'PIN:</strong> (\d+)', create.text)
                
                if account_match:
                    print(f"   📋 Account Number: {account_match.group(1)}")
                if pin_match:
                    print(f"   🔑 PIN: {pin_match.group(1)}")
                    
                print("\n🎉 SUCCESS: Account creation is working!")
                return True
            else:
                print("   ⚠️  Account creation completed but check response")
                # Save response for debugging
                with open('last_response.html', 'w') as f:
                    f.write(create.text)
                print("   Response saved to last_response.html")
                return False
        else:
            print("   ❌ Account creation failed")
            return False
    else:
        print("   ❌ Admin login failed")
        return False

if __name__ == "__main__":
    success = test_account_creation()
    if success:
        print("\n✨ All tests passed!")
    else:
        print("\n⚠️  Check the response file for details")