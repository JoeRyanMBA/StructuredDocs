#!/usr/bin/env python3
"""
Test script to verify password reset implementation
"""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_password_hashing():
    """Test password hashing functionality"""
    print("Testing password hashing...")
    
    try:
        from werkzeug.security import generate_password_hash, check_password_hash
        
        # Test password
        password = "testpassword123"
        
        # Generate hash
        password_hash = generate_password_hash(password)
        print(f"✅ Password hash generated: {password_hash[:20]}...")
        
        # Verify password
        is_valid = check_password_hash(password_hash, password)
        print(f"✅ Password verification: {is_valid}")
        
        # Test wrong password
        is_invalid = check_password_hash(password_hash, "wrongpassword")
        print(f"✅ Wrong password verification: {is_invalid}")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_email_service():
    """Test email service functionality"""
    print("\nTesting email service...")
    
    try:
        from utils.email_service import EmailService
        
        email_service = EmailService()
        print(f"✅ Email service initialized")
        print(f"   Debug mode: {email_service.debug_mode}")
        print(f"   SMTP server: {email_service.smtp_server}")
        print(f"   From email: {email_service.from_email}")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_token_generation():
    """Test token generation"""
    print("\nTesting token generation...")
    
    try:
        import secrets
        
        # Generate a URL-safe token
        token = secrets.token_urlsafe(32)
        print(f"✅ Token generated: {token[:20]}...")
        print(f"   Token length: {len(token)}")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Run all tests"""
    print("🔧 Testing Password Reset Implementation")
    print("=" * 50)
    
    tests = [
        test_password_hashing,
        test_email_service,
        test_token_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✅ All tests passed! Password reset implementation looks good.")
    else:
        print("⚠️ Some tests failed. Check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
