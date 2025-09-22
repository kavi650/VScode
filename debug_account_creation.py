import requests
import sys

def test_account_creation():
    session = requests.Session()
    
    # Step 1: Login as admin
    print("=== STEP 1: Admin Login ===")
    login_url = "http://localhost:5000/admin_login"
    login_data = {"username": "admin", "password": "a123"}
    
    response = session.post(login_url, data=login_data)
    print(f"Login Status: {response.status_code}")
    print(f"Login URL: {response.url}")
    
    if response.status_code != 200 or 'admin_dashboard' not in response.url:
        print("❌ Admin login failed!")
        return False
    
    print("✅ Admin login successful!")
    
    # Step 2: Get the account creation form first
    print("\n=== STEP 2: Get Account Creation Form ===")
    form_url = "http://localhost:5000/enhanced_create_account"
    form_response = session.get(form_url)
    
    print(f"Form Status: {form_response.status_code}")
    if form_response.status_code != 200:
        print("❌ Could not access account creation form")
        return False
    
    print("✅ Account creation form accessible")
    
    # Step 3: Submit account creation form
    print("\n=== STEP 3: Submit Account Creation ===")
    
    # Get all form fields from the HTML to see what's expected
    import re
    form_html = form_response.text
    
    # Find all input fields
    input_fields = re.findall(r'<input[^>]*name="([^"]*)"[^>]*>', form_html)
    select_fields = re.findall(r'<select[^>]*name="([^"]*)"[^>]*>', form_html)
    
    print("Expected form fields:")
    for field in input_fields + select_fields:
        print(f"  - {field}")
    
    # Prepare account data
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
    
    print(f"\nSubmitting data: {account_data}")
    
    create_response = session.post(form_url, data=account_data)
    
    print(f"\nAccount Creation Response:")
    print(f"Status Code: {create_response.status_code}")
    print(f"URL: {create_response.url}")
    print(f"Response Length: {len(create_response.text)} characters")
    
    # Check if it's the same form again (indicating validation error)
    if 'name="name"' in create_response.text and len(create_response.text) > 5000:
        print("❌ ERROR: Form was returned (likely validation error)")
        
        # Look for error messages
        error_patterns = [
            r'<div[^>]*class="[^"]*error[^"]*"[^>]*>([^<]*)</div>',
            r'<div[^>]*class="[^"]*alert[^"]*"[^>]*>([^<]*)</div>',
            r'<p[^>]*class="[^"]*error[^"]*"[^>]*>([^<]*)</p>'
        ]
        
        errors_found = []
        for pattern in error_patterns:
            matches = re.findall(pattern, create_response.text, re.IGNORECASE)
            errors_found.extend(matches)
        
        if errors_found:
            print("Error messages found:")
            for error in errors_found:
                print(f"  - {error.strip()}")
        else:
            print("No obvious error messages found in response")
            
        # Save the response for debugging
        with open('debug_account_response.html', 'w', encoding='utf-8') as f:
            f.write(create_response.text)
        print("Response saved to debug_account_response.html")
        
    elif 'successfully' in create_response.text:
        print("✅ SUCCESS: Account created successfully!")
        
        # Look for account number
        account_match = re.search(r'Account Number: (\d+)', create_response.text)
        if account_match:
            print(f"Account Number: {account_match.group(1)}")
        
    else:
        print("❓ Unclear response - checking content...")
        print("Response preview:", create_response.text[:200])
    
    return True

if __name__ == "__main__":
    test_account_creation()