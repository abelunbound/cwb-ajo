#!/usr/bin/env python3
"""
Test Task 14: Implement Group Membership System
Tests that the group membership system is complete and functional.
"""

import sys
import unittest
import psycopg2
from datetime import datetime, date
from decimal import Decimal
import time
from functions.database import get_ajo_db_connection
from functions.group_membership_service import (
    add_member_to_group, remove_member_from_group, update_member_role,
    get_group_members, get_user_groups, update_payment_position,
    get_group_admin_count, is_user_group_member
)

class TestTask14GroupMembershipSystem(unittest.TestCase):
    """Test that Task 14 group membership system is complete."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database connection and test data."""
        cls.connection = get_ajo_db_connection()
        cls.cursor = cls.connection.cursor()
        
        # Generate unique timestamp for test data
        cls.timestamp = str(int(time.time()))
        cls.test_email_pattern = f'task14test{cls.timestamp}'
        
        # Clean up any existing test data (correct order for foreign keys)
        try:
            cls.cursor.execute("DELETE FROM group_members WHERE group_id IN (SELECT id FROM ajo_groups WHERE name LIKE %s)", (f'%{cls.test_email_pattern}%',))
            cls.cursor.execute("DELETE FROM ajo_groups WHERE name LIKE %s", (f'%{cls.test_email_pattern}%',))
            cls.cursor.execute("DELETE FROM users WHERE email LIKE %s", (f'%{cls.test_email_pattern}%',))
            cls.connection.commit()
        except psycopg2.Error:
            cls.connection.rollback()  # Ignore cleanup errors
        
        # Create test users with timestamp-based emails
        cls.test_users = []
        for i in range(3):
            cls.cursor.execute("""
                INSERT INTO users (email, password_hash, full_name, verification_status)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (f'testuser{i}@{cls.test_email_pattern}.com', 'dummy_hash', f'Test User {i}', 'verified'))
            cls.test_users.append(cls.cursor.fetchone()[0])
        
        # Create test group with timestamp-based name
        cls.cursor.execute("""
            INSERT INTO ajo_groups (name, contribution_amount, frequency, start_date, 
                                  duration_months, max_members, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (f'Test Group {cls.test_email_pattern}', Decimal('100.00'), 'monthly', date(2024, 8, 1), 6, 5, cls.test_users[0]))
        cls.test_group_id = cls.cursor.fetchone()[0]
        
        cls.connection.commit()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test data and close connection."""
        try:
            # Clean up in correct order (foreign key constraints)
            cls.cursor.execute("DELETE FROM group_members WHERE group_id IN (SELECT id FROM ajo_groups WHERE name LIKE %s)", (f'%{cls.test_email_pattern}%',))
            cls.cursor.execute("DELETE FROM ajo_groups WHERE name LIKE %s", (f'%{cls.test_email_pattern}%',))
            cls.cursor.execute("DELETE FROM users WHERE email LIKE %s", (f'%{cls.test_email_pattern}%',))
            cls.connection.commit()
        except Exception as e:
            print(f"Cleanup warning: {e}")
            cls.connection.rollback()
        finally:
            cls.cursor.close()
            cls.connection.close()
    
    def test_group_members_table_exists(self):
        """Test that group_members table exists with all required fields."""
        required_fields = [
            'id', 'group_id', 'user_id', 'role', 'payment_position', 
            'join_date', 'status', 'created_at'
        ]
        
        self.cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'group_members'
        """)
        existing_fields = [row[0] for row in self.cursor.fetchall()]
        
        for field in required_fields:
            with self.subTest(field=field):
                self.assertIn(field, existing_fields,
                            f"Required field '{field}' missing from group_members table")
    
    def test_group_members_constraints(self):
        """Test that group_members table has proper constraints."""
        expected_constraints = [
            'group_members_pkey',  # Primary key
            'group_members_group_id_user_id_key',  # Unique membership
            'group_members_group_id_payment_position_key',  # Unique payment position
            'group_members_group_id_fkey',  # Foreign key to groups
            'group_members_user_id_fkey',  # Foreign key to users
            'group_members_role_check',  # Role validation
            'group_members_status_check',  # Status validation
            'group_members_payment_position_check'  # Payment position validation
        ]
        
        self.cursor.execute("""
            SELECT conname
            FROM pg_constraint 
            WHERE conrelid = 'group_members'::regclass
        """)
        existing_constraints = [row[0] for row in self.cursor.fetchall()]
        
        for constraint in expected_constraints:
            with self.subTest(constraint=constraint):
                self.assertIn(constraint, existing_constraints,
                            f"Required constraint '{constraint}' missing from group_members table")
    
    def test_group_members_indexes(self):
        """Test that group_members table has performance indexes."""
        expected_indexes = [
            'group_members_pkey',
            'idx_group_members_group_id',
            'idx_group_members_user_id'
        ]
        
        self.cursor.execute("""
            SELECT indexname
            FROM pg_indexes 
            WHERE tablename = 'group_members'
        """)
        existing_indexes = [row[0] for row in self.cursor.fetchall()]
        
        for index in expected_indexes:
            with self.subTest(index=index):
                self.assertIn(index, existing_indexes,
                            f"Required index '{index}' missing from group_members table")
    
    def test_add_member_to_group(self):
        """Test adding members to a group."""
        # Add first member as admin
        result = add_member_to_group(self.test_group_id, self.test_users[0], 'admin')
        self.assertTrue(result['success'])
        self.assertIn('member_id', result)
        
        # Add second member
        result = add_member_to_group(self.test_group_id, self.test_users[1], 'member')
        self.assertTrue(result['success'])
        
        # Test duplicate member
        result = add_member_to_group(self.test_group_id, self.test_users[0], 'member')
        self.assertFalse(result['success'])
        self.assertIn('already a member', result['error'])
    
    def test_get_group_members(self):
        """Test retrieving group members."""
        # Add a member first
        add_member_to_group(self.test_group_id, self.test_users[2], 'member')
        
        # Get members
        members = get_group_members(self.test_group_id)
        self.assertIsNotNone(members)
        self.assertGreater(len(members), 0)
        
        # Check member structure
        member = members[0]
        required_fields = ['id', 'user_id', 'full_name', 'role', 'payment_position']
        for field in required_fields:
            with self.subTest(field=field):
                self.assertIn(field, member)
    
    def test_update_member_role(self):
        """Test updating member roles."""
        # Add a member first
        add_member_to_group(self.test_group_id, self.test_users[1], 'member')
        
        # Update role
        result = update_member_role(self.test_group_id, self.test_users[1], 'admin')
        self.assertTrue(result['success'])
        
        # Verify role updated
        membership = is_user_group_member(self.test_group_id, self.test_users[1])
        self.assertIsNotNone(membership)
        self.assertEqual(membership['role'], 'admin')
    
    def test_payment_position_assignment(self):
        """Test payment position assignment."""
        # Create new group for this test
        self.cursor.execute("""
            INSERT INTO ajo_groups (name, contribution_amount, frequency, start_date, 
                                  duration_months, max_members, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (f'Test Position Group {self.test_email_pattern}', Decimal('50.00'), 'weekly', date(2024, 9, 1), 4, 3, self.test_users[0]))
        group_id = self.cursor.fetchone()[0]
        self.connection.commit()
        
        # Add members and check positions
        for i, user_id in enumerate(self.test_users):
            result = add_member_to_group(group_id, user_id, 'member')
            self.assertTrue(result['success'])
            self.assertEqual(result['payment_position'], i + 1)
        
        # Clean up
        self.cursor.execute("DELETE FROM group_members WHERE group_id = %s", (group_id,))
        self.cursor.execute("DELETE FROM ajo_groups WHERE id = %s", (group_id,))
        self.connection.commit()
    
    def test_membership_validation(self):
        """Test membership validation and business rules."""
        # Test role constraint validation
        try:
            self.cursor.execute("""
                INSERT INTO group_members (group_id, user_id, role, payment_position)
                VALUES (%s, %s, %s, %s)
            """, (self.test_group_id, self.test_users[0], 'invalid_role', 10))
            self.fail("Should have rejected invalid role")
        except psycopg2.IntegrityError:
            self.connection.rollback()  # Expected behavior
        
        # Test status constraint validation
        try:
            self.cursor.execute("""
                INSERT INTO group_members (group_id, user_id, role, payment_position, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (self.test_group_id, self.test_users[0], 'member', 11, 'invalid_status'))
            self.fail("Should have rejected invalid status")
        except psycopg2.IntegrityError:
            self.connection.rollback()  # Expected behavior
        
        # Test payment position constraint (must be positive)
        try:
            self.cursor.execute("""
                INSERT INTO group_members (group_id, user_id, role, payment_position)
                VALUES (%s, %s, %s, %s)
            """, (self.test_group_id, self.test_users[0], 'member', 0))
            self.fail("Should have rejected zero payment position")
        except psycopg2.IntegrityError:
            self.connection.rollback()  # Expected behavior
    
    def test_unique_constraints(self):
        """Test unique constraints for membership and payment positions."""
        # Test duplicate payment position fails
        add_member_to_group(self.test_group_id, self.test_users[0], 'member')
        members = get_group_members(self.test_group_id)
        
        if members:
            existing_position = members[0]['payment_position']
            try:
                self.cursor.execute("""
                    INSERT INTO group_members (group_id, user_id, role, payment_position)
                    VALUES (%s, %s, %s, %s)
                """, (self.test_group_id, self.test_users[1], 'member', existing_position))
                self.fail("Should reject duplicate payment position")
            except psycopg2.IntegrityError:
                self.connection.rollback()  # Expected
    
    def test_foreign_key_constraints(self):
        """Test foreign key constraints for group_id and user_id."""
        # Test invalid group_id
        try:
            self.cursor.execute("""
                INSERT INTO group_members (group_id, user_id, role, payment_position)
                VALUES (%s, %s, %s, %s)
            """, (99999, self.test_users[0], 'member', 30))
            self.fail("Should have rejected invalid group_id")
        except psycopg2.IntegrityError:
            self.connection.rollback()  # Expected behavior
        
        # Test invalid user_id
        try:
            self.cursor.execute("""
                INSERT INTO group_members (group_id, user_id, role, payment_position)
                VALUES (%s, %s, %s, %s)
            """, (self.test_group_id, 99999, 'member', 31))
            self.fail("Should have rejected invalid user_id")
        except psycopg2.IntegrityError:
            self.connection.rollback()  # Expected behavior
    
    def test_is_user_group_member(self):
        """Test checking if user is group member."""
        # Check if user is already a member first, if not add them
        membership = is_user_group_member(self.test_group_id, self.test_users[2])
        if not membership:
            result = add_member_to_group(self.test_group_id, self.test_users[2], 'member')
            if not result['success'] and 'already a member' not in result['error']:
                self.fail(f"Failed to add member: {result['error']}")
        
        # Test positive case
        membership = is_user_group_member(self.test_group_id, self.test_users[2])
        self.assertIsNotNone(membership)
        self.assertEqual(membership['role'], 'member')
        self.assertIn('payment_position', membership)
        
        # Test negative case
        membership = is_user_group_member(self.test_group_id, 99999)
        self.assertIsNone(membership)
    
    def test_service_functions_integration(self):
        """Test integration of all service functions."""
        # Create a new group for comprehensive testing
        self.cursor.execute("""
            INSERT INTO ajo_groups (name, contribution_amount, frequency, start_date, 
                                  duration_months, max_members, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, ('Test Integration Group', Decimal('75.00'), 'monthly', date(2024, 10, 1), 8, 2, self.test_users[0]))
        integration_group_id = self.cursor.fetchone()[0]
        self.connection.commit()
        
        # Test complete workflow
        # 1. Add admin
        result = add_member_to_group(integration_group_id, self.test_users[0], 'admin')
        self.assertTrue(result['success'])
        
        # 2. Add regular member
        result = add_member_to_group(integration_group_id, self.test_users[1], 'member')
        self.assertTrue(result['success'])
        
        # 3. Verify group is full (max 2 members)
        result = add_member_to_group(integration_group_id, self.test_users[2], 'member')
        self.assertFalse(result['success'])
        self.assertIn('full', result['error'])
        
        # 4. Get all members
        members = get_group_members(integration_group_id)
        self.assertEqual(len(members), 2)
        
        # Clean up
        self.cursor.execute("DELETE FROM group_members WHERE group_id = %s", (integration_group_id,))
        self.cursor.execute("DELETE FROM ajo_groups WHERE id = %s", (integration_group_id,))
        self.connection.commit()

if __name__ == '__main__':
    print("Testing Task 14: Implement Group Membership System")
    print("=" * 60)
    
    # Run the tests
    unittest.main(verbosity=2) 