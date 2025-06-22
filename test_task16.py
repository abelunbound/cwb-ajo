#!/usr/bin/env python3
"""
Test Task 16: Implement Payment Distribution System
Tests that the payment distribution system is complete and functional.
"""

import sys
import unittest
import psycopg2
from datetime import datetime, date, timedelta
from decimal import Decimal
import time
from functions.database import get_ajo_db_connection
from functions.distribution_service import (
    create_distribution, complete_distribution, fail_distribution,
    get_group_distributions, get_user_distributions, get_distribution_summary,
    get_next_recipient, calculate_distribution_amount, get_distribution_history,
    validate_distribution_eligibility
)

class TestTask16PaymentDistribution(unittest.TestCase):
    """Test that Task 16 payment distribution system is complete."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database connection and test data."""
        cls.connection = get_ajo_db_connection()
        cls.cursor = cls.connection.cursor()
        
        # Generate unique timestamp for test data
        cls.timestamp = str(int(time.time()))
        cls.test_email_pattern = f'task16test{cls.timestamp}'
        
        # Clean up any existing test data (correct order for foreign keys)
        try:
            cls.cursor.execute("DELETE FROM distributions WHERE group_id IN (SELECT id FROM ajo_groups WHERE name LIKE %s)", (f'%{cls.test_email_pattern}%',))
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
        """, (f'Test Group {cls.test_email_pattern}', Decimal('200.00'), 'monthly', date(2024, 8, 1), 6, 5, cls.test_users[0]))
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
            cls.cursor.execute("DELETE FROM distributions WHERE group_id IN (SELECT id FROM ajo_groups WHERE name LIKE %s)", (f'%{cls.test_email_pattern}%',))
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
    
    def test_distributions_table_exists(self):
        """Test that distributions table exists with all required fields."""
        required_fields = [
            'id', 'group_id', 'recipient_id', 'amount', 'distribution_date',
            'transaction_id', 'status', 'notes', 'created_at', 'updated_at'
        ]
        
        self.cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'distributions'
        """)
        existing_fields = [row[0] for row in self.cursor.fetchall()]
        
        for field in required_fields:
            with self.subTest(field=field):
                self.assertIn(field, existing_fields,
                            f"Required field '{field}' missing from distributions table")
    
    def test_distributions_constraints(self):
        """Test that distributions table has proper constraints."""
        expected_constraints = [
            'distributions_pkey',  # Primary key
            'distributions_group_id_fkey',  # Foreign key to groups
            'distributions_recipient_id_fkey',  # Foreign key to users
            'distributions_amount_check',  # Amount validation
            'distributions_status_check'  # Status validation
        ]
        
        self.cursor.execute("""
            SELECT conname
            FROM pg_constraint 
            WHERE conrelid = 'distributions'::regclass
        """)
        existing_constraints = [row[0] for row in self.cursor.fetchall()]
        
        for constraint in expected_constraints:
            with self.subTest(constraint=constraint):
                self.assertIn(constraint, existing_constraints,
                            f"Required constraint '{constraint}' missing from distributions table")
    
    def test_distributions_indexes(self):
        """Test that distributions table has performance indexes."""
        expected_indexes = [
            'distributions_pkey',
            'idx_distributions_group_id',
            'idx_distributions_recipient_id',
            'idx_distributions_status'
        ]
        
        self.cursor.execute("""
            SELECT indexname
            FROM pg_indexes 
            WHERE tablename = 'distributions'
        """)
        existing_indexes = [row[0] for row in self.cursor.fetchall()]
        
        for index in expected_indexes:
            with self.subTest(index=index):
                self.assertIn(index, existing_indexes,
                            f"Required index '{index}' missing from distributions table")
    
    def test_create_distribution(self):
        """Test creating distribution records."""
        distribution_date = date.today()
        
        # Test successful distribution creation
        result = create_distribution(
            self.test_group_id, 
            self.test_users[0], 
            Decimal('800.00'),  # 4 members * 200
            distribution_date,
            'Monthly distribution'
        )
        self.assertTrue(result['success'])
        self.assertIn('distribution_id', result)
        self.assertEqual(result['amount'], Decimal('800.00'))
        self.assertEqual(result['status'], 'pending')
        
        # Test excessive amount
        result = create_distribution(
            self.test_group_id, 
            self.test_users[1], 
            Decimal('2000.00'),  # Too much
            distribution_date
        )
        self.assertFalse(result['success'])
        self.assertIn('exceeds maximum possible', result['error'])
        
        # Test non-member distribution
        self.cursor.execute("""
            INSERT INTO users (email, password_hash, full_name, verification_status)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (f'nonmember@{self.test_email_pattern}.com', 'dummy_hash', 'Non Member', 'verified'))
        non_member_id = self.cursor.fetchone()[0]
        self.connection.commit()
        
        result = create_distribution(
            self.test_group_id, 
            non_member_id, 
            Decimal('800.00'), 
            distribution_date
        )
        self.assertFalse(result['success'])
        self.assertIn('not an active member', result['error'])
    
    def test_complete_distribution(self):
        """Test completing distributions."""
        # Create a distribution first
        distribution_date = date.today()
        result = create_distribution(
            self.test_group_id, 
            self.test_users[1], 
            Decimal('800.00'), 
            distribution_date
        )
        distribution_id = result['distribution_id']
        
        # Complete the distribution
        complete_result = complete_distribution(
            distribution_id, 
            'DIST123456'
        )
        self.assertTrue(complete_result['success'])
        self.assertEqual(complete_result['status'], 'completed')
        self.assertEqual(complete_result['transaction_id'], 'DIST123456')
        
        # Test completing already completed distribution
        complete_again = complete_distribution(distribution_id, 'DIST789')
        self.assertFalse(complete_again['success'])
        self.assertIn('already processed', complete_again['error'])
    
    def test_fail_distribution(self):
        """Test failing distributions."""
        # Create a distribution first
        distribution_date = date.today()
        result = create_distribution(
            self.test_group_id, 
            self.test_users[2], 
            Decimal('800.00'), 
            distribution_date
        )
        distribution_id = result['distribution_id']
        
        # Fail the distribution
        fail_result = fail_distribution(
            distribution_id, 
            'Insufficient funds'
        )
        self.assertTrue(fail_result['success'])
        self.assertEqual(fail_result['status'], 'failed')
        self.assertEqual(fail_result['failure_reason'], 'Insufficient funds')
    
    def test_get_group_distributions(self):
        """Test retrieving group distributions."""
        # Create some distributions
        distribution_date = date.today()
        create_distribution(
            self.test_group_id, 
            self.test_users[3], 
            Decimal('800.00'), 
            distribution_date
        )
        
        # Get all group distributions
        distributions = get_group_distributions(self.test_group_id)
        self.assertIsInstance(distributions, list)
        self.assertGreater(len(distributions), 0)
        
        # Check distribution structure
        dist = distributions[0]
        required_fields = ['id', 'recipient_id', 'recipient_name', 'amount', 'status']
        for field in required_fields:
            with self.subTest(field=field):
                self.assertIn(field, dist)
        
        # Test status filter
        pending_distributions = get_group_distributions(self.test_group_id, 'pending')
        self.assertIsInstance(pending_distributions, list)
    
    def test_get_user_distributions(self):
        """Test retrieving user distributions."""
        # Get user distributions
        distributions = get_user_distributions(self.test_users[0])
        self.assertIsInstance(distributions, list)
        
        # Check distribution structure if any exist
        if distributions:
            dist = distributions[0]
            required_fields = ['id', 'group_id', 'group_name', 'amount', 'status']
            for field in required_fields:
                with self.subTest(field=field):
                    self.assertIn(field, dist)
        
        # Test group-specific filter
        group_distributions = get_user_distributions(self.test_users[0], self.test_group_id)
        self.assertIsInstance(group_distributions, list)
    
    def test_distribution_summary(self):
        """Test distribution summary generation."""
        # Create various distributions
        distribution_date = date.today()
        
        # Create and complete one distribution
        result1 = create_distribution(
            self.test_group_id, 
            self.test_users[1], 
            Decimal('800.00'), 
            distribution_date
        )
        complete_distribution(result1['distribution_id'], 'DIST001')
        
        # Create pending distribution
        create_distribution(
            self.test_group_id, 
            self.test_users[2], 
            Decimal('800.00'), 
            distribution_date
        )
        
        # Get summary
        summary = get_distribution_summary(self.test_group_id)
        self.assertIn('group_id', summary)
        self.assertIn('total_distributions', summary)
        self.assertIn('completed_distributions', summary)
        self.assertIn('pending_distributions', summary)
        self.assertIn('total_distributed', summary)
        self.assertIn('recent_distributions', summary)
        
        # Verify counts
        self.assertGreaterEqual(summary['total_distributions'], 2)
        self.assertGreaterEqual(summary['completed_distributions'], 1)
    
    def test_get_next_recipient(self):
        """Test getting next recipient in payment order."""
        # Get next recipient
        next_recipient = get_next_recipient(self.test_group_id)
        self.assertTrue(next_recipient['success'])
        self.assertIn('user_id', next_recipient)
        self.assertIn('full_name', next_recipient)
        self.assertIn('payment_position', next_recipient)
        self.assertTrue(next_recipient['is_next'])
        
        # Should be first member (payment position 1)
        self.assertEqual(next_recipient['payment_position'], 1)
    
    def test_calculate_distribution_amount(self):
        """Test distribution amount calculation."""
        # Calculate distribution amount
        calculation = calculate_distribution_amount(self.test_group_id)
        self.assertTrue(calculation['success'])
        self.assertIn('group_id', calculation)
        self.assertIn('total_collected', calculation)
        self.assertIn('expected_total', calculation)
        self.assertIn('available_for_distribution', calculation)
        self.assertIn('active_members', calculation)
        
        # Verify expected total calculation
        self.assertEqual(calculation['expected_total'], Decimal('800.00'))  # 4 members * 200
        self.assertEqual(calculation['active_members'], 4)
    
    def test_get_distribution_history(self):
        """Test getting distribution history."""
        # Create a distribution for history
        distribution_date = date.today()
        create_distribution(
            self.test_group_id, 
            self.test_users[0], 
            Decimal('800.00'), 
            distribution_date,
            'Test distribution for history'
        )
        
        # Get history
        history = get_distribution_history(self.test_group_id)
        self.assertIsInstance(history, list)
        
        if history:
            dist = history[0]
            required_fields = ['id', 'recipient_name', 'amount', 'status', 'group_name']
            for field in required_fields:
                with self.subTest(field=field):
                    self.assertIn(field, dist)
    
    def test_validate_distribution_eligibility(self):
        """Test distribution eligibility validation."""
        # Test eligible member
        eligibility = validate_distribution_eligibility(self.test_group_id, self.test_users[0])
        self.assertTrue(eligibility['eligible'])
        self.assertIn('member_id', eligibility)
        self.assertIn('payment_position', eligibility)
        self.assertIn('contribution_rate', eligibility)
        
        # Test non-member
        self.cursor.execute("""
            INSERT INTO users (email, password_hash, full_name, verification_status)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (f'nonmember2@{self.test_email_pattern}.com', 'dummy_hash', 'Non Member 2', 'verified'))
        non_member_id = self.cursor.fetchone()[0]
        self.connection.commit()
        
        eligibility = validate_distribution_eligibility(self.test_group_id, non_member_id)
        self.assertFalse(eligibility['eligible'])
        self.assertIn('not a member', eligibility['reason'])
    
    def test_validation_constraints(self):
        """Test database validation constraints."""
        # Test negative amount constraint
        try:
            self.cursor.execute("""
                INSERT INTO distributions (group_id, recipient_id, amount, distribution_date, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (self.test_group_id, self.test_users[0], Decimal('-10.00'), date.today(), 'pending'))
            self.fail("Should have rejected negative amount")
        except psycopg2.IntegrityError:
            self.connection.rollback()  # Expected behavior
        
        # Test invalid status constraint
        try:
            self.cursor.execute("""
                INSERT INTO distributions (group_id, recipient_id, amount, distribution_date, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (self.test_group_id, self.test_users[0], Decimal('800.00'), date.today(), 'invalid_status'))
            self.fail("Should have rejected invalid status")
        except psycopg2.IntegrityError:
            self.connection.rollback()  # Expected behavior
    
    def test_foreign_key_constraints(self):
        """Test foreign key constraints."""
        # Test invalid group_id
        try:
            self.cursor.execute("""
                INSERT INTO distributions (group_id, recipient_id, amount, distribution_date, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (99999, self.test_users[0], Decimal('800.00'), date.today(), 'pending'))
            self.fail("Should have rejected invalid group_id")
        except psycopg2.IntegrityError:
            self.connection.rollback()  # Expected behavior
        
        # Test invalid recipient_id
        try:
            self.cursor.execute("""
                INSERT INTO distributions (group_id, recipient_id, amount, distribution_date, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (self.test_group_id, 99999, Decimal('800.00'), date.today(), 'pending'))
            self.fail("Should have rejected invalid recipient_id")
        except psycopg2.IntegrityError:
            self.connection.rollback()  # Expected behavior
    
    def test_relationship_with_contributions(self):
        """Test relationship between distributions and contributions."""
        # This test verifies that distributions are logically related to contributions
        # by checking that distribution amounts make sense relative to contribution patterns
        
        distribution_date = date.today()
        
        # Create a distribution
        result = create_distribution(
            self.test_group_id, 
            self.test_users[0], 
            Decimal('800.00'), 
            distribution_date
        )
        self.assertTrue(result['success'])
        
        # Verify the distribution exists
        distributions = get_group_distributions(self.test_group_id)
        self.assertGreater(len(distributions), 0)
        
        # Verify distribution amount is reasonable for group size
        calculation = calculate_distribution_amount(self.test_group_id)
        self.assertTrue(calculation['success'])
        self.assertEqual(calculation['expected_total'], Decimal('800.00'))
    
    def test_business_logic_constraints(self):
        """Test business logic constraints."""
        distribution_date = date.today()
        
        # Test that distribution amount doesn't exceed reasonable limits
        result = create_distribution(
            self.test_group_id, 
            self.test_users[0], 
            Decimal('800.00'),  # Exactly what's expected
            distribution_date
        )
        self.assertTrue(result['success'])
        
        # Test that excessive amounts are rejected
        result = create_distribution(
            self.test_group_id, 
            self.test_users[1], 
            Decimal('1000.00'),  # More than possible
            distribution_date
        )
        self.assertFalse(result['success'])
    
    def test_service_functions_integration(self):
        """Test integration of all service functions."""
        distribution_date = date.today()
        
        # Create distribution
        result = create_distribution(
            self.test_group_id, 
            self.test_users[1], 
            Decimal('800.00'), 
            distribution_date,
            'Integration test distribution'
        )
        self.assertTrue(result['success'])
        distribution_id = result['distribution_id']
        
        # Verify it appears in group distributions
        group_distributions = get_group_distributions(self.test_group_id)
        self.assertTrue(any(d['id'] == distribution_id for d in group_distributions))
        
        # Verify it appears in user distributions
        user_distributions = get_user_distributions(self.test_users[1])
        self.assertTrue(any(d['id'] == distribution_id for d in user_distributions))
        
        # Complete the distribution
        complete_result = complete_distribution(distribution_id, 'INTEG123')
        self.assertTrue(complete_result['success'])
        
        # Verify status updated in summary
        summary = get_distribution_summary(self.test_group_id)
        self.assertGreater(summary['completed_distributions'], 0)
        self.assertGreater(summary['total_distributed'], 0)


if __name__ == '__main__':
    print("Testing Task 16: Implement Payment Distribution System")
    print("=" * 60)
    unittest.main(verbosity=2)