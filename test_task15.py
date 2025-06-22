#!/usr/bin/env python3
"""
Test Task 15: Create Contribution Tracking System
Tests that the contribution tracking system is complete and functional.
"""

import sys
import unittest
import psycopg2
from datetime import datetime, date, timedelta
from decimal import Decimal
import time
from functions.database import get_ajo_db_connection
from functions.contribution_service import (
    record_contribution, mark_contribution_paid, get_user_contributions,
    get_group_contributions, get_overdue_contributions, update_overdue_contributions,
    get_contribution_summary, cancel_contribution, bulk_create_contributions
)

class TestTask15ContributionTracking(unittest.TestCase):
    """Test that Task 15 contribution tracking system is complete."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database connection and test data."""
        cls.connection = get_ajo_db_connection()
        cls.cursor = cls.connection.cursor()
        
        # Generate unique timestamp for test data
        cls.timestamp = str(int(time.time()))
        cls.test_email_pattern = f'task15test{cls.timestamp}'
        
        # Clean up any existing test data (correct order for foreign keys)
        try:
            cls.cursor.execute("DELETE FROM contributions WHERE group_id IN (SELECT id FROM ajo_groups WHERE name LIKE %s)", (f'%{cls.test_email_pattern}%',))
            cls.cursor.execute("DELETE FROM group_members WHERE group_id IN (SELECT id FROM ajo_groups WHERE name LIKE %s)", (f'%{cls.test_email_pattern}%',))
            cls.cursor.execute("DELETE FROM ajo_groups WHERE name LIKE %s", (f'%{cls.test_email_pattern}%',))
            cls.cursor.execute("DELETE FROM users WHERE email LIKE %s", (f'%{cls.test_email_pattern}%',))
            cls.connection.commit()
        except psycopg2.Error:
            cls.connection.rollback()  # Ignore cleanup errors
        
        # Create test users with timestamp-based emails
        cls.test_users = []
        for i in range(4):
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
        
        # Add members to the group
        for i, user_id in enumerate(cls.test_users):
            role = 'admin' if i == 0 else 'member'
            cls.cursor.execute("""
                INSERT INTO group_members (group_id, user_id, role, payment_position, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (cls.test_group_id, user_id, role, i + 1, 'active'))
        
        cls.connection.commit()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test data and close connection."""
        try:
            # Clean up in correct order (foreign key constraints)
            cls.cursor.execute("DELETE FROM contributions WHERE group_id IN (SELECT id FROM ajo_groups WHERE name LIKE %s)", (f'%{cls.test_email_pattern}%',))
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
    
    def test_contributions_table_exists(self):
        """Test that contributions table exists with all required fields."""
        required_fields = [
            'id', 'group_id', 'user_id', 'amount', 'due_date', 'paid_date',
            'payment_method', 'transaction_id', 'status', 'created_at', 'updated_at'
        ]
        
        self.cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'contributions'
        """)
        existing_fields = [row[0] for row in self.cursor.fetchall()]
        
        for field in required_fields:
            with self.subTest(field=field):
                self.assertIn(field, existing_fields,
                            f"Required field '{field}' missing from contributions table")
    
    def test_contributions_constraints(self):
        """Test that contributions table has proper constraints."""
        expected_constraints = [
            'contributions_pkey',  # Primary key
            'contributions_group_id_fkey',  # Foreign key to groups
            'contributions_user_id_fkey',  # Foreign key to users
            'contributions_amount_check',  # Amount validation
            'contributions_status_check'  # Status validation
        ]
        
        self.cursor.execute("""
            SELECT conname
            FROM pg_constraint 
            WHERE conrelid = 'contributions'::regclass
        """)
        existing_constraints = [row[0] for row in self.cursor.fetchall()]
        
        for constraint in expected_constraints:
            with self.subTest(constraint=constraint):
                self.assertIn(constraint, existing_constraints,
                            f"Required constraint '{constraint}' missing from contributions table")
    
    def test_contributions_indexes(self):
        """Test that contributions table has performance indexes."""
        expected_indexes = [
            'contributions_pkey',
            'idx_contributions_group_id',
            'idx_contributions_user_id',
            'idx_contributions_status',
            'idx_contributions_due_date'
        ]
        
        self.cursor.execute("""
            SELECT indexname
            FROM pg_indexes 
            WHERE tablename = 'contributions'
        """)
        existing_indexes = [row[0] for row in self.cursor.fetchall()]
        
        for index in expected_indexes:
            with self.subTest(index=index):
                self.assertIn(index, existing_indexes,
                            f"Required index '{index}' missing from contributions table")
    
    def test_record_contribution(self):
        """Test recording individual contributions."""
        due_date = date.today() + timedelta(days=30)
        
        # Test successful contribution recording
        result = record_contribution(
            self.test_group_id, 
            self.test_users[0], 
            Decimal('100.00'), 
            due_date,
            'bank_transfer'
        )
        self.assertTrue(result['success'])
        self.assertIn('contribution_id', result)
        self.assertEqual(result['amount'], Decimal('100.00'))
        self.assertEqual(result['status'], 'pending')
        
        # Test invalid amount
        result = record_contribution(
            self.test_group_id, 
            self.test_users[1], 
            Decimal('50.00'),  # Wrong amount
            due_date
        )
        self.assertFalse(result['success'])
        self.assertIn('Contribution amount must be', result['error'])
        
        # Test non-member contribution
        self.cursor.execute("""
            INSERT INTO users (email, password_hash, full_name, verification_status)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (f'nonmember@{self.test_email_pattern}.com', 'dummy_hash', 'Non Member', 'verified'))
        non_member_id = self.cursor.fetchone()[0]
        self.connection.commit()
        
        result = record_contribution(
            self.test_group_id, 
            non_member_id, 
            Decimal('100.00'), 
            due_date
        )
        self.assertFalse(result['success'])
        self.assertIn('not an active member', result['error'])
    
    def test_mark_contribution_paid(self):
        """Test marking contributions as paid."""
        # Create a contribution first
        due_date = date.today() + timedelta(days=30)
        result = record_contribution(
            self.test_group_id, 
            self.test_users[1], 
            Decimal('100.00'), 
            due_date
        )
        contribution_id = result['contribution_id']
        
        # Mark as paid
        paid_result = mark_contribution_paid(
            contribution_id, 
            'TXN123456', 
            date.today()
        )
        self.assertTrue(paid_result['success'])
        self.assertEqual(paid_result['status'], 'paid')
        self.assertEqual(paid_result['transaction_id'], 'TXN123456')
        
        # Test marking already paid contribution
        paid_again = mark_contribution_paid(contribution_id, 'TXN789')
        self.assertFalse(paid_again['success'])
        self.assertIn('already processed', paid_again['error'])
    
    def test_get_user_contributions(self):
        """Test retrieving user contributions."""
        # Create some contributions
        due_date = date.today() + timedelta(days=30)
        record_contribution(
            self.test_group_id, 
            self.test_users[2], 
            Decimal('100.00'), 
            due_date
        )
        
        # Get user contributions
        contributions = get_user_contributions(self.test_users[2])
        self.assertIsInstance(contributions, list)
        self.assertGreater(len(contributions), 0)
        
        # Check contribution structure
        contrib = contributions[0]
        required_fields = ['id', 'group_id', 'group_name', 'amount', 'due_date', 'status']
        for field in required_fields:
            with self.subTest(field=field):
                self.assertIn(field, contrib)
        
        # Test group-specific filter
        group_contributions = get_user_contributions(self.test_users[2], self.test_group_id)
        self.assertIsInstance(group_contributions, list)
    
    def test_get_group_contributions(self):
        """Test retrieving group contributions."""
        # Create some contributions
        due_date = date.today() + timedelta(days=30)
        record_contribution(
            self.test_group_id, 
            self.test_users[3], 
            Decimal('100.00'), 
            due_date
        )
        
        # Get all group contributions
        contributions = get_group_contributions(self.test_group_id)
        self.assertIsInstance(contributions, list)
        self.assertGreater(len(contributions), 0)
        
        # Check contribution structure
        contrib = contributions[0]
        required_fields = ['id', 'user_id', 'user_name', 'user_email', 'amount', 'status']
        for field in required_fields:
            with self.subTest(field=field):
                self.assertIn(field, contrib)
        
        # Test status filter
        pending_contributions = get_group_contributions(self.test_group_id, 'pending')
        self.assertIsInstance(pending_contributions, list)
    
    def test_overdue_contributions(self):
        """Test overdue contribution handling."""
        # Create an overdue contribution
        overdue_date = date.today() - timedelta(days=5)
        record_contribution(
            self.test_group_id, 
            self.test_users[0], 
            Decimal('100.00'), 
            overdue_date
        )
        
        # Get overdue contributions
        overdue = get_overdue_contributions()
        self.assertIsInstance(overdue, list)
        
        # Update overdue status
        update_result = update_overdue_contributions()
        self.assertTrue(update_result['success'])
        self.assertGreaterEqual(update_result['updated_count'], 0)
    
    def test_contribution_summary(self):
        """Test contribution summary generation."""
        # Create various contributions
        due_date = date.today() + timedelta(days=30)
        
        # Create and pay one contribution
        result1 = record_contribution(
            self.test_group_id, 
            self.test_users[1], 
            Decimal('100.00'), 
            due_date
        )
        mark_contribution_paid(result1['contribution_id'], 'TXN001')
        
        # Create pending contribution
        record_contribution(
            self.test_group_id, 
            self.test_users[2], 
            Decimal('100.00'), 
            due_date
        )
        
        # Get summary
        summary = get_contribution_summary(self.test_group_id)
        self.assertIn('group_id', summary)
        self.assertIn('total_contributions', summary)
        self.assertIn('paid_contributions', summary)
        self.assertIn('pending_contributions', summary)
        self.assertIn('total_paid', summary)
        self.assertIn('recent_activity', summary)
        
        # Verify counts
        self.assertGreaterEqual(summary['total_contributions'], 2)
        self.assertGreaterEqual(summary['paid_contributions'], 1)
    
    def test_cancel_contribution(self):
        """Test contribution cancellation."""
        # Create a contribution
        due_date = date.today() + timedelta(days=30)
        result = record_contribution(
            self.test_group_id, 
            self.test_users[3], 
            Decimal('100.00'), 
            due_date
        )
        contribution_id = result['contribution_id']
        
        # Cancel the contribution
        cancel_result = cancel_contribution(contribution_id, 'User requested cancellation')
        self.assertTrue(cancel_result['success'])
        self.assertEqual(cancel_result['status'], 'cancelled')
        self.assertEqual(cancel_result['reason'], 'User requested cancellation')
        
        # Test cancelling already cancelled contribution
        cancel_again = cancel_contribution(contribution_id)
        self.assertFalse(cancel_again['success'])
    
    def test_bulk_create_contributions(self):
        """Test bulk contribution creation."""
        due_date = date.today() + timedelta(days=30)
        
        # Create contributions for all group members
        result = bulk_create_contributions(self.test_group_id, due_date)
        self.assertTrue(result['success'])
        self.assertEqual(result['group_id'], self.test_group_id)
        self.assertGreaterEqual(result['created_count'], len(self.test_users))
        self.assertIn('contributions', result)
        
        # Verify contributions were created
        for contrib in result['contributions']:
            self.assertIn('id', contrib)
            self.assertIn('user_id', contrib)
            self.assertEqual(contrib['amount'], Decimal('100.00'))
            self.assertEqual(contrib['due_date'], due_date)
        
        # Test with exclusions
        exclude_result = bulk_create_contributions(
            self.test_group_id, 
            due_date + timedelta(days=30),
            exclude_user_ids=[self.test_users[0]]
        )
        self.assertTrue(exclude_result['success'])
        self.assertEqual(exclude_result['created_count'], len(self.test_users) - 1)
    
    def test_validation_constraints(self):
        """Test database validation constraints."""
        # Test negative amount constraint
        try:
            self.cursor.execute("""
                INSERT INTO contributions (group_id, user_id, amount, due_date, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (self.test_group_id, self.test_users[0], Decimal('-10.00'), date.today(), 'pending'))
            self.fail("Should have rejected negative amount")
        except psycopg2.IntegrityError:
            self.connection.rollback()  # Expected behavior
        
        # Test invalid status constraint
        try:
            self.cursor.execute("""
                INSERT INTO contributions (group_id, user_id, amount, due_date, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (self.test_group_id, self.test_users[0], Decimal('100.00'), date.today(), 'invalid_status'))
            self.fail("Should have rejected invalid status")
        except psycopg2.IntegrityError:
            self.connection.rollback()  # Expected behavior
    
    def test_foreign_key_constraints(self):
        """Test foreign key constraints."""
        # Test invalid group_id
        try:
            self.cursor.execute("""
                INSERT INTO contributions (group_id, user_id, amount, due_date, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (99999, self.test_users[0], Decimal('100.00'), date.today(), 'pending'))
            self.fail("Should have rejected invalid group_id")
        except psycopg2.IntegrityError:
            self.connection.rollback()  # Expected behavior
        
        # Test invalid user_id
        try:
            self.cursor.execute("""
                INSERT INTO contributions (group_id, user_id, amount, due_date, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (self.test_group_id, 99999, Decimal('100.00'), date.today(), 'pending'))
            self.fail("Should have rejected invalid user_id")
        except psycopg2.IntegrityError:
            self.connection.rollback()  # Expected behavior
    
    def test_service_functions_integration(self):
        """Test integration of all service functions."""
        due_date = date.today() + timedelta(days=30)
        
        # Create contribution
        result = record_contribution(
            self.test_group_id, 
            self.test_users[1], 
            Decimal('100.00'), 
            due_date,
            'mobile_money'
        )
        self.assertTrue(result['success'])
        contribution_id = result['contribution_id']
        
        # Verify it appears in user contributions
        user_contributions = get_user_contributions(self.test_users[1])
        self.assertTrue(any(c['id'] == contribution_id for c in user_contributions))
        
        # Verify it appears in group contributions
        group_contributions = get_group_contributions(self.test_group_id)
        self.assertTrue(any(c['id'] == contribution_id for c in group_contributions))
        
        # Mark as paid
        mark_result = mark_contribution_paid(contribution_id, 'TXN123')
        self.assertTrue(mark_result['success'])
        
        # Verify status updated in summary
        summary = get_contribution_summary(self.test_group_id)
        self.assertGreater(summary['paid_contributions'], 0)
        self.assertGreater(summary['total_paid'], 0)


if __name__ == '__main__':
    print("Testing Task 15: Create Contribution Tracking System")
    print("=" * 60)
    unittest.main(verbosity=2)