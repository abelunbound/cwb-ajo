#!/usr/bin/env python3
"""Test suite for Task 2: Enhanced Password Security.

This module tests password strength validation and user registration
functionality added to auth.py.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auth import validate_password_strength, register_user, USERS_DB


def test_password_strength_validation():
    """Test password strength validation function."""
    print("🧪 Testing password strength validation...")
    
    # Test cases: (password, should_be_valid, description)
    test_cases = [
        ("Password123", True, "Valid password with all requirements"),
        ("password123", False, "Missing uppercase letter"),
        ("PASSWORD123", False, "Missing lowercase letter"),
        ("Password", False, "Missing number"),
        ("Pass1", False, "Too short (less than 8 characters)"),
        ("", False, "Empty password"),
        ("MySecurePass1", True, "Valid longer password"),
        ("Test123!", True, "Valid password with special character"),
    ]
    
    passed = 0
    total = len(test_cases)
    
    for password, expected_valid, description in test_cases:
        result = validate_password_strength(password)
        actual_valid = result['valid']
        
        if actual_valid == expected_valid:
            print(f"✅ {description}")
            passed += 1
        else:
            print(f"❌ {description}")
            print(f"   Expected: {expected_valid}, Got: {actual_valid}")
            if not actual_valid:
                print(f"   Errors: {result['errors']}")
    
    print(f"\n📊 Password validation tests: {passed}/{total} passed")
    return passed == total


def test_user_registration():
    """Test user registration function."""
    print("\n🧪 Testing user registration...")
    
    # Store original USERS_DB state
    original_users = USERS_DB.copy()
    
    try:
        # Test cases: (email, password, password_confirm, name, should_succeed, description)
        test_cases = [
            ("test@example.com", "ValidPass123", "ValidPass123", "Test User", True, "Valid registration"),
            ("test@example.com", "ValidPass456", "ValidPass456", "Test User 2", False, "Duplicate email"),
            ("test2@example.com", "ValidPass123", "DifferentPass", "Test User 2", False, "Password mismatch"),
            ("test3@example.com", "weak", "weak", "Test User 3", False, "Weak password"),
            ("test4@example.com", "StrongPass789", "StrongPass789", "Test User 4", True, "Another valid registration"),
        ]
        
        passed = 0
        total = len(test_cases)
        
        for email, password, password_confirm, name, expected_success, description in test_cases:
            result = register_user(email, password, password_confirm, name)
            actual_success = result['success']
            
            if actual_success == expected_success:
                print(f"✅ {description}")
                passed += 1
            else:
                print(f"❌ {description}")
                print(f"   Expected success: {expected_success}, Got: {actual_success}")
                if not actual_success:
                    print(f"   Error: {result['error']}")
        
        print(f"\n📊 User registration tests: {passed}/{total} passed")
        return passed == total
        
    finally:
        # Restore original USERS_DB state
        USERS_DB.clear()
        USERS_DB.update(original_users)


def test_integration():
    """Test integration of password validation with existing auth system."""
    print("\n🧪 Testing integration with existing auth...")
    
    # Store original USERS_DB state
    original_users = USERS_DB.copy()
    
    try:
        # Register a new user with strong password
        result = register_user("newuser@example.com", "SecurePass123", "SecurePass123", "New User")
        
        if result['success']:
            print("✅ User registration successful")
            
            # Try to validate the new user
            from auth import validate_user
            user_data = validate_user("newuser@example.com", "SecurePass123")
            
            if user_data and user_data['email'] == "newuser@example.com":
                print("✅ New user login successful")
                return True
            else:
                print("❌ New user login failed")
                return False
        else:
            print(f"❌ User registration failed: {result['error']}")
            return False
            
    finally:
        # Restore original USERS_DB state
        USERS_DB.clear()
        USERS_DB.update(original_users)


def main():
    """Run all tests for Task 2."""
    print("🚀 Task 2: Enhanced Password Security - Test Suite")
    print("=" * 60)
    
    test1_passed = test_password_strength_validation()
    test2_passed = test_user_registration()
    test3_passed = test_integration()
    
    print("\n" + "=" * 60)
    print("📋 SUMMARY:")
    print(f"✅ Password Strength Validation: {'PASS' if test1_passed else 'FAIL'}")
    print(f"✅ User Registration: {'PASS' if test2_passed else 'FAIL'}")
    print(f"✅ Integration Test: {'PASS' if test3_passed else 'FAIL'}")
    
    print("\n🌐 BROWSER TESTING:")
    print("To test the complete registration flow in browser:")
    print("1. Start the app: python app.py")
    print("2. Go to http://127.0.0.1:8050/")
    print("3. Click 'Sign up' to switch to registration mode")
    print("4. Test password validation with weak passwords")
    print("5. Register with strong password and verify login")
    
    all_passed = test1_passed and test2_passed and test3_passed
    print(f"\n🎯 Overall Result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 