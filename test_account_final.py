#!/usr/bin/env python3
"""
Final test script to verify account creation is working properly.
"""

import requests
import json
import time

def test_account_creation():
    """Test the complete account creation flow"""
    
    # Base URL
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Account Creation Flow")
    print("=" * 40)
    
    # Step 1: Login as admin
    print("1. Logging in as admin...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        login_response = requests.post(f"{base_url}/admin_login", data=login_data)
        print(f"   Login status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print("   ❌ Admin login failed")
            return False
            
        print("   ✅ Admin login successful")
        
    except Exception as e:
        print(f"   ❌ Admin login error: {e}")
        return False
    
    # Step 2: Create new account
    print("\n2. Creating new account...")
    
    # Generate unique email with timestamp
    timestamp = int(time.time())
    account_data = {
        'name': f'Test User {timestamp}',
        'email': f'testuser{timestamp}@example.com',
        'mobile': '1234567890',
        'address': '123 Test Street, Test City',
        'dob': '1990-01-01',
        'aadhar': '123456789012',
        'pin': '1234',
        'preferred_currency': 'INR'
    }
    
    try:
        create_response = requests.post(f"{base_url}/enhanced_create_account", data=account_data)
        print(f"   Account creation status: {create_response.status_code}")
        
        if create_response.status_code != 200:
            print("   ❌ Account creation failed")
            return False
            
        # Check if response contains success indicators
        response_text = create_response.text
        if 'Account Created Successfully' in response_text:
            print("   ✅ Account created successfully")
            
            # Try to extract account number from response
            if 'Account Number:' in response_text:
                print("   ✅ Account number displayed in response")
            else:
                print("   ⚠️  Account number not found in response")
                
            if 'email_status' in response_text:
                print("   ✅ Email status displayed in response")
            else:
                print("   ℹ️  Email status not displayed (this is okay)")
                
        else:
            print("   ❌ Success message not found in response")
            print(f"   Response preview: {response_text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Account creation error: {e}")
        return False
    
    print("\n3. ✅ All tests passed!")
    return True

if __name__ == "__main__":
    success = test_account_creation()
    if success:
        print("\n🎉 Account creation is working correctly!")
    else:
        print("\n❌ Account creation has issues that need to be fixed.")