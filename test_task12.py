#!/usr/bin/env python3
"""
Test Task 12: Create User Profile Enhancement
Tests that user authentication has been migrated from in-memory to PostgreSQL
with enhanced profile fields.
"""

import sys
import unittest
import psycopg2
from functions.database import get_ajo_db_connection
from functions.user_service import (
    create_user, get_user_by_email, get_user_by_id, 
    authenticate_user, update_user_profile
)
from auth import validate_user, register_user, validate_password_strength
from werkzeug.security import generate_password_hash

class TestTask12UserProfileEnhancement(unittest.TestCase):
    """Test that Task 12 user profile enhancement is complete."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database connection."""
        cls.connection = get_ajo_db_connection()
        cls.cursor = cls.connection.cursor()
        
        # Clean up any existing test users
        cls.cursor.execute("DELETE FROM users WHERE email LIKE '%test%'")
        cls.connection.commit()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test data and close connection."""
        # Clean up test users
        cls.cursor.execute("DELETE FROM users WHERE email LIKE '%test%'")
        cls.connection.commit()
        cls.cursor.close()
        cls.connection.close()
    
    def test_users_table_has_enhanced_fields(self):
        """Test that users table has all required enhanced fields from Task 12."""
        required_fields = [
            'id', 'email', 'password_hash', 'full_name', 'created_at', 'updated_at',
            'phone_number', 'bank_account_details', 'credit_score',
            'verification_status', 'preferred_payment_method'
        ]
        
        self.cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users'
        """)
        existing_fields = [row[0] for row in self.cursor.fetchall()]
        
        for field in required_fields:
            with self.subTest(field=field):
                self.assertIn(field, existing_fields,
                            f"Required field '{field}' missing from users table")
    
    def test_user_creation_with_enhanced_fields(self):
        """Test creating users with enhanced profile fields."""
        password_hash = generate_password_hash('TestPass123')
        
        result = create_user(
            email='test_enhanced@test.com',
            password_hash=password_hash,
            full_name='Enhanced Test User',
            phone_number='+44123456789',
            verification_status='pending',
            preferred_payment_method='card'
        )
        
        self.assertTrue(result['success'])
        self.assertIsInstance(result['user_id'], int)
        
        # Verify user was created with correct fields
        user = get_user_by_email('test_enhanced@test.com')
        self.assertIsNotNone(user)
        self.assertEqual(user['full_name'], 'Enhanced Test User')
        self.assertEqual(user['phone_number'], '+44123456789')
        self.assertEqual(user['verification_status'], 'pending')
        self.assertEqual(user['preferred_payment_method'], 'card')
    
    def test_user_authentication_from_database(self):
        """Test that user authentication works from PostgreSQL database."""
        # Create test user
        password_hash = generate_password_hash('AuthTest123')
        result = create_user(
            email='test_auth@test.com',
            password_hash=password_hash,
            full_name='Auth Test User'
        )
        self.assertTrue(result['success'])
        
        # Test successful authentication
        user = authenticate_user('test_auth@test.com', 'AuthTest123')
        self.assertIsNotNone(user)
        self.assertEqual(user['email'], 'test_auth@test.com')
        self.assertEqual(user['name'], 'Auth Test User')  # Compatibility field
        self.assertEqual(user['full_name'], 'Auth Test User')
        
        # Test failed authentication
        user = authenticate_user('test_auth@test.com', 'WrongPassword')
        self.assertIsNone(user)
    
    def test_auth_module_uses_database(self):
        """Test that auth.py functions use PostgreSQL instead of in-memory."""
        # Test registration creates user in database
        result = register_user(
            'test_register@test.com', 
            'RegisterPass123', 
            'RegisterPass123', 
            'Register Test User'
        )
        self.assertTrue(result['success'])
        self.assertIn('user_id', result)
        
        # Verify user exists in database
        user = get_user_by_email('test_register@test.com')
        self.assertIsNotNone(user)
        self.assertEqual(user['full_name'], 'Register Test User')
        
        # Test login works with database user
        validated_user = validate_user('test_register@test.com', 'RegisterPass123')
        self.assertIsNotNone(validated_user)
        self.assertEqual(validated_user['name'], 'Register Test User')
    
    def test_password_strength_validation(self):
        """Test password strength validation still works."""
        # Test strong password
        result = validate_password_strength('StrongPass123')
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
        
        # Test weak passwords
        weak_passwords = [
            'short',  # Too short
            'nouppercase123',  # No uppercase
            'NOLOWERCASE123',  # No lowercase  
            'NoNumbers',  # No numbers
        ]
        
        for password in weak_passwords:
            with self.subTest(password=password):
                result = validate_password_strength(password)
                self.assertFalse(result['valid'])
                self.assertGreater(len(result['errors']), 0)
    
    def test_user_profile_updates(self):
        """Test updating user profile fields."""
        # Create test user
        password_hash = generate_password_hash('UpdateTest123')
        result = create_user(
            email='test_update@test.com',
            password_hash=password_hash,
            full_name='Update Test User'
        )
        user_id = result['user_id']
        
        # Update profile
        update_result = update_user_profile(
            user_id,
            phone_number='+44987654321',
            credit_score=750,
            verification_status='verified'
        )
        self.assertTrue(update_result['success'])
        
        # Verify updates
        user = get_user_by_id(user_id)
        self.assertEqual(user['phone_number'], '+44987654321')
        self.assertEqual(user['credit_score'], 750)
        self.assertEqual(user['verification_status'], 'verified')
    
    def test_demo_users_migrated(self):
        """Test that demo users have been migrated to database."""
        # Check demo user exists
        demo_user = get_user_by_email('demo@example.com')
        self.assertIsNotNone(demo_user)
        self.assertEqual(demo_user['full_name'], 'Abel')
        self.assertEqual(demo_user['verification_status'], 'verified')
        
        # Check admin user exists
        admin_user = get_user_by_email('admin@example.com')
        self.assertIsNotNone(admin_user)
        self.assertEqual(admin_user['full_name'], 'Admin User')
        
        # Test demo user can login
        validated_demo = validate_user('demo@example.com', 'password123')
        self.assertIsNotNone(validated_demo)
        self.assertEqual(validated_demo['name'], 'Abel')
    
    def test_user_registration_prevents_duplicates(self):
        """Test that user registration prevents duplicate emails."""
        # Create first user
        result1 = register_user(
            'duplicate@test.com',
            'TestPass123',
            'TestPass123',
            'First User'
        )
        self.assertTrue(result1['success'])
        
        # Try to create duplicate
        result2 = register_user(
            'duplicate@test.com',
            'DifferentPass123',
            'DifferentPass123',
            'Second User'
        )
        self.assertFalse(result2['success'])
        self.assertIn('already exists', result2['error'].lower())
    
    def test_database_connection_to_ajo_db(self):
        """Test that user functions connect to ajo-platform-db."""
        conn = get_ajo_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        self.assertEqual(db_name, 'ajo-platform-db')

if __name__ == '__main__':
    print("Testing Task 12: User Profile Enhancement (PostgreSQL Migration)")
    print("=" * 70)
    
    # Run the tests
    unittest.main(verbosity=2) 