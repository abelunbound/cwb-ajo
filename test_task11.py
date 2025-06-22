#!/usr/bin/env python3
"""
Test Task 11: Design Ajo-Specific Database Schema
Tests that all required tables exist with proper constraints and indexes.
"""

import sys
import unittest
import psycopg2
from functions.database import get_config

class TestTask11AjoSchema(unittest.TestCase):
    """Test that Task 11 Ajo-specific database schema is complete."""
    
    @classmethod
    def setUpClass(cls):
        """Set up database connection for tests."""
        cls.config = get_config()
        cls.connection = psycopg2.connect(
            dbname=cls.config.AJO_DB_NAME,
            user=cls.config.AJO_DB_USER,
            password=cls.config.AJO_DB_PASSWORD,
            host=cls.config.AJO_DB_HOST,
            port=cls.config.AJO_DB_PORT
        )
        cls.cursor = cls.connection.cursor()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up database connection."""
        cls.cursor.close()
        cls.connection.close()
    
    def test_required_tables_exist(self):
        """Test that all required tables from Task 11 exist."""
        required_tables = [
            'ajo_groups',
            'group_members', 
            'contributions',
            'payments',
            'distributions',
            'users'
        ]
        
        self.cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        existing_tables = [row[0] for row in self.cursor.fetchall()]
        
        for table in required_tables:
            with self.subTest(table=table):
                self.assertIn(table, existing_tables, 
                            f"Required table '{table}' is missing from database")
    
    def test_ajo_groups_schema(self):
        """Test ajo_groups table has required fields."""
        required_columns = [
            'id', 'name', 'description', 'contribution_amount', 
            'frequency', 'start_date', 'duration_months', 'max_members',
            'status', 'created_by', 'created_at'
        ]
        
        self.cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'ajo_groups'
        """)
        existing_columns = [row[0] for row in self.cursor.fetchall()]
        
        for column in required_columns:
            with self.subTest(column=column):
                self.assertIn(column, existing_columns,
                            f"Required column '{column}' missing from ajo_groups")
    
    def test_group_members_schema(self):
        """Test group_members table has required fields."""
        required_columns = [
            'id', 'group_id', 'user_id', 'role', 'payment_position',
            'join_date', 'status', 'created_at'
        ]
        
        self.cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'group_members'
        """)
        existing_columns = [row[0] for row in self.cursor.fetchall()]
        
        for column in required_columns:
            with self.subTest(column=column):
                self.assertIn(column, existing_columns,
                            f"Required column '{column}' missing from group_members")
    
    def test_contributions_schema(self):
        """Test contributions table has required fields."""
        required_columns = [
            'id', 'group_id', 'user_id', 'amount', 'due_date', 'paid_date',
            'payment_method', 'transaction_id', 'status'
        ]
        
        self.cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'contributions'
        """)
        existing_columns = [row[0] for row in self.cursor.fetchall()]
        
        for column in required_columns:
            with self.subTest(column=column):
                self.assertIn(column, existing_columns,
                            f"Required column '{column}' missing from contributions")
    
    def test_payments_schema(self):
        """Test payments table has required fields."""
        required_columns = [
            'id', 'contribution_id', 'distribution_id', 'provider',
            'provider_payment_id', 'amount', 'currency', 'status',
            'verification_status', 'created_at'
        ]
        
        self.cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'payments'
        """)
        existing_columns = [row[0] for row in self.cursor.fetchall()]
        
        for column in required_columns:
            with self.subTest(column=column):
                self.assertIn(column, existing_columns,
                            f"Required column '{column}' missing from payments")
    
    def test_foreign_key_constraints(self):
        """Test that foreign key relationships exist."""
        # Test group_members references ajo_groups
        self.cursor.execute("""
            SELECT COUNT(*) FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = 'group_members' 
            AND tc.constraint_type = 'FOREIGN KEY'
            AND kcu.column_name = 'group_id'
        """)
        fk_count = self.cursor.fetchone()[0]
        self.assertGreater(fk_count, 0, "group_members.group_id foreign key missing")
        
        # Test contributions references ajo_groups and group_members
        self.cursor.execute("""
            SELECT COUNT(*) FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = 'contributions' 
            AND tc.constraint_type = 'FOREIGN KEY'
            AND kcu.column_name IN ('group_id', 'user_id')
        """)
        fk_count = self.cursor.fetchone()[0]
        self.assertGreaterEqual(fk_count, 1, "contributions foreign keys missing")
    
    def test_payments_constraints(self):
        """Test payments table has proper constraints."""
        # Test amount positive constraint
        self.cursor.execute("""
            SELECT COUNT(*) FROM information_schema.check_constraints cc
            JOIN information_schema.constraint_column_usage ccu
            ON cc.constraint_name = ccu.constraint_name
            WHERE ccu.table_name = 'payments'
            AND cc.check_clause LIKE '%amount%>%0%'
        """)
        constraint_count = self.cursor.fetchone()[0]
        self.assertGreater(constraint_count, 0, "payments amount positive constraint missing")
    
    def test_payments_indexes(self):
        """Test payments table has performance indexes."""
        self.cursor.execute("""
            SELECT COUNT(*) FROM pg_indexes 
            WHERE tablename = 'payments'
            AND indexname LIKE 'idx_payments_%'
        """)
        index_count = self.cursor.fetchone()[0]
        self.assertGreaterEqual(index_count, 3, "payments table missing performance indexes")
    
    def test_database_connection_to_correct_db(self):
        """Test we're connected to the correct database."""
        self.cursor.execute("SELECT current_database();")
        db_name = self.cursor.fetchone()[0]
        self.assertEqual(db_name, self.config.AJO_DB_NAME, 
                        f"Connected to wrong database: {db_name}, expected: {self.config.AJO_DB_NAME}")

if __name__ == '__main__':
    print("Testing Task 11: Ajo-Specific Database Schema")
    print("=" * 50)
    
    # Run the tests
    unittest.main(verbosity=2) 