#!/usr/bin/env python3
"""
Test Task 13: Implement Group Management Tables
Tests that the ajo_groups table meets all requirements and functions correctly.
"""

import sys
import unittest
import psycopg2
from datetime import datetime, date
from decimal import Decimal
from functions.database import get_ajo_db_connection

class TestTask13GroupManagementTables(unittest.TestCase):
    """Test that Task 13 group management tables are complete."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database connection."""
        cls.connection = get_ajo_db_connection()
        cls.cursor = cls.connection.cursor()
        
        # Clean up any existing test groups
        cls.cursor.execute("DELETE FROM ajo_groups WHERE name LIKE '%test%'")
        cls.connection.commit()
        
        # Create a test user for foreign key relationships
        cls.cursor.execute("""
            INSERT INTO users (email, password_hash, full_name, verification_status)
            VALUES ('testuser@task13.com', 'dummy_hash', 'Test User', 'verified')
            ON CONFLICT (email) DO UPDATE SET full_name = 'Test User'
            RETURNING id
        """)
        cls.test_user_id = cls.cursor.fetchone()[0]
        cls.connection.commit()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test data and close connection."""
        try:
            # Clean up test groups first (due to foreign key constraint)
            cls.cursor.execute("DELETE FROM ajo_groups WHERE name LIKE '%test%' OR name LIKE 'Test Group%'")
            cls.cursor.execute("DELETE FROM users WHERE email = 'testuser@task13.com'")
            cls.connection.commit()
        except Exception as e:
            print(f"Cleanup warning: {e}")
            cls.connection.rollback()
        finally:
            cls.cursor.close()
            cls.connection.close()
    
    def test_ajo_groups_table_exists(self):
        """Test that ajo_groups table exists."""
        self.cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'ajo_groups'
        """)
        result = self.cursor.fetchone()
        self.assertIsNotNone(result, "ajo_groups table does not exist")
        self.assertEqual(result[0], 'ajo_groups')
    
    def test_ajo_groups_required_fields(self):
        """Test that ajo_groups table has all required fields from Task 13."""
        required_fields = [
            'id', 'name', 'description', 'contribution_amount', 'frequency',
            'start_date', 'duration_months', 'max_members', 'status',
            'created_by', 'created_at', 'end_date'
        ]
        
        self.cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'ajo_groups'
        """)
        existing_fields = [row[0] for row in self.cursor.fetchall()]
        
        for field in required_fields:
            with self.subTest(field=field):
                self.assertIn(field, existing_fields,
                            f"Required field '{field}' missing from ajo_groups table")
    
    def test_ajo_groups_field_types(self):
        """Test that ajo_groups fields have correct data types."""
        expected_types = {
            'id': 'integer',
            'name': 'character varying',
            'contribution_amount': 'numeric',
            'frequency': 'character varying',
            'start_date': 'date',
            'duration_months': 'integer',
            'max_members': 'integer',
            'created_by': 'integer'
        }
        
        self.cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns 
            WHERE table_name = 'ajo_groups'
        """)
        actual_types = {row[0]: row[1] for row in self.cursor.fetchall()}
        
        for field, expected_type in expected_types.items():
            with self.subTest(field=field):
                self.assertEqual(actual_types.get(field), expected_type,
                               f"Field '{field}' has wrong type. Expected: {expected_type}, Got: {actual_types.get(field)}")
    
    def test_ajo_groups_indexes(self):
        """Test that ajo_groups table has performance indexes."""
        expected_indexes = [
            'ajo_groups_pkey',
            'idx_ajo_groups_created_by',
            'idx_ajo_groups_status',
            'idx_ajo_groups_end_date'
        ]
        
        self.cursor.execute("""
            SELECT indexname
            FROM pg_indexes 
            WHERE tablename = 'ajo_groups'
        """)
        existing_indexes = [row[0] for row in self.cursor.fetchall()]
        
        for index in expected_indexes:
            with self.subTest(index=index):
                self.assertIn(index, existing_indexes,
                            f"Required index '{index}' missing from ajo_groups table")
    
    def test_group_creation_with_all_fields(self):
        """Test creating a group with all required fields."""
        group_data = {
            'name': 'Test Group Complete',
            'description': 'A complete test group',
            'contribution_amount': Decimal('100.00'),
            'frequency': 'monthly',
            'start_date': date(2024, 2, 1),
            'duration_months': 12,
            'max_members': 8,
            'status': 'active',
            'created_by': self.test_user_id
        }
        
        insert_query = """
            INSERT INTO ajo_groups (name, description, contribution_amount, frequency,
                                  start_date, duration_months, max_members, status, created_by)
            VALUES (%(name)s, %(description)s, %(contribution_amount)s, %(frequency)s,
                   %(start_date)s, %(duration_months)s, %(max_members)s, %(status)s, %(created_by)s)
            RETURNING id;
        """
        
        self.cursor.execute(insert_query, group_data)
        group_id = self.cursor.fetchone()[0]
        self.connection.commit()
        
        # Verify the group was created correctly
        self.cursor.execute("SELECT name, contribution_amount, frequency FROM ajo_groups WHERE id = %s", (group_id,))
        result = self.cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], group_data['name'])
        self.assertEqual(result[1], group_data['contribution_amount'])
        self.assertEqual(result[2], group_data['frequency'])
    
    def test_group_creation_minimal_fields(self):
        """Test creating a group with only required fields."""
        group_data = {
            'name': 'Test Group Minimal',
            'contribution_amount': Decimal('50.00'),
            'frequency': 'weekly',
            'start_date': date(2024, 3, 1),
            'duration_months': 6,
            'max_members': 5,
            'created_by': self.test_user_id
        }
        
        insert_query = """
            INSERT INTO ajo_groups (name, contribution_amount, frequency,
                                  start_date, duration_months, max_members, created_by)
            VALUES (%(name)s, %(contribution_amount)s, %(frequency)s,
                   %(start_date)s, %(duration_months)s, %(max_members)s, %(created_by)s)
            RETURNING id;
        """
        
        self.cursor.execute(insert_query, group_data)
        group_id = self.cursor.fetchone()[0]
        self.connection.commit()
        
        # Verify the group was created with default values
        self.cursor.execute("SELECT name, status FROM ajo_groups WHERE id = %s", (group_id,))
        result = self.cursor.fetchone()
        
        self.assertIsNotNone(result)
        self.assertEqual(result[0], group_data['name'])
        self.assertEqual(result[1], 'active')  # Default status
    
    def test_group_retrieval_by_criteria(self):
        """Test retrieving groups by various criteria."""
        # Create test groups
        test_groups = [
            ('Test Group Weekly', Decimal('50.00'), 'weekly', 'active'),
            ('Test Group Monthly', Decimal('100.00'), 'monthly', 'completed')
        ]
        
        for name, amount, frequency, status in test_groups:
            insert_query = """
                INSERT INTO ajo_groups (name, contribution_amount, frequency,
                                      start_date, duration_months, max_members, status, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.cursor.execute(insert_query, (
                name, amount, frequency, date(2024, 4, 1), 6, 5, status, self.test_user_id
            ))
        
        self.connection.commit()
        
        # Test retrieval by frequency
        self.cursor.execute("SELECT COUNT(*) FROM ajo_groups WHERE frequency = 'weekly' AND name LIKE 'Test Group Weekly%'")
        weekly_count = self.cursor.fetchone()[0]
        self.assertGreaterEqual(weekly_count, 1)
        
        # Test retrieval by status
        self.cursor.execute("SELECT COUNT(*) FROM ajo_groups WHERE status = 'active' AND name LIKE 'Test Group%'")
        active_count = self.cursor.fetchone()[0]
        self.assertGreaterEqual(active_count, 1)
    
    def test_foreign_key_relationship(self):
        """Test that created_by foreign key relationship works."""
        # Valid foreign key should work
        group_data = {
            'name': 'Test Group FK Valid',
            'contribution_amount': Decimal('75.00'),
            'frequency': 'monthly',
            'start_date': date(2024, 6, 1),
            'duration_months': 4,
            'max_members': 5,
            'created_by': self.test_user_id
        }
        
        insert_query = """
            INSERT INTO ajo_groups (name, contribution_amount, frequency,
                                  start_date, duration_months, max_members, created_by)
            VALUES (%(name)s, %(contribution_amount)s, %(frequency)s,
                   %(start_date)s, %(duration_months)s, %(max_members)s, %(created_by)s)
            RETURNING id;
        """
        
        self.cursor.execute(insert_query, group_data)
        group_id = self.cursor.fetchone()[0]
        self.connection.commit()
        self.assertIsNotNone(group_id)
        
        # Invalid foreign key should fail
        invalid_group_data = group_data.copy()
        invalid_group_data['name'] = 'Test Group FK Invalid'
        invalid_group_data['created_by'] = 99999  # Non-existent user ID
        
        with self.assertRaises(psycopg2.IntegrityError):
            self.cursor.execute(insert_query, invalid_group_data)
            self.connection.commit()
        
        # Rollback the failed transaction
        self.connection.rollback()
    
    def test_end_date_auto_calculation(self):
        """Test that end_date is automatically calculated from start_date + duration_months."""
        group_data = {
            'name': 'Test Group End Date',
            'contribution_amount': Decimal('200.00'),
            'frequency': 'monthly',
            'start_date': date(2024, 6, 15),
            'duration_months': 8,
            'max_members': 6,
            'created_by': self.test_user_id
        }
        
        insert_query = """
            INSERT INTO ajo_groups (name, contribution_amount, frequency,
                                  start_date, duration_months, max_members, created_by)
            VALUES (%(name)s, %(contribution_amount)s, %(frequency)s,
                   %(start_date)s, %(duration_months)s, %(max_members)s, %(created_by)s)
            RETURNING id, start_date, duration_months, end_date;
        """
        
        self.cursor.execute(insert_query, group_data)
        result = self.cursor.fetchone()
        self.connection.commit()
        
        group_id = result[0]
        start_date = result[1]
        duration_months = result[2]
        end_date = result[3]
        
        # Verify end_date is calculated correctly (start_date + duration_months)
        expected_end_date = date(2025, 2, 15)  # 2024-06-15 + 8 months
        self.assertEqual(end_date, expected_end_date)
        
        # Test updating duration recalculates end_date
        self.cursor.execute("""
            UPDATE ajo_groups 
            SET duration_months = 12 
            WHERE id = %s
            RETURNING end_date
        """, (group_id,))
        
        new_end_date = self.cursor.fetchone()[0]
        expected_new_end_date = date(2025, 6, 15)  # 2024-06-15 + 12 months
        self.assertEqual(new_end_date, expected_new_end_date)
        
        self.connection.commit()

if __name__ == '__main__':
    print("Testing Task 13: Implement Group Management Tables")
    print("=" * 60)
    
    # Run the tests
    unittest.main(verbosity=2) 