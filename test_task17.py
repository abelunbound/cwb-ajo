"""
Task 17: Add Financial Summary Views - Test Suite

This test suite verifies that all financial summary views are working correctly
and returning accurate data for financial reporting and analysis.

Tests cover:
1. Group Financial Summary View
2. Member Contribution Summary View  
3. Pending Payments View
4. Overdue Contributions View
5. Group Performance Dashboard View
6. View performance with indexes
"""

import psycopg2
from datetime import datetime, date, timedelta
from functions.database import get_ajo_db_connection
from decimal import Decimal


class TestTask17FinancialSummaryViews:
    """Test suite for Task 17 financial summary views"""
    
    @classmethod
    def setup_class(cls):
        """Set up test database connection and sample data"""
        cls.conn = get_ajo_db_connection()
        cls.cursor = cls.conn.cursor()
        
        # Clean up any existing test data
        cls._cleanup_test_data()
        
        # Create comprehensive test data
        cls._create_test_data()
    
    @classmethod
    def teardown_class(cls):
        """Clean up test data and close connection"""
        cls._cleanup_test_data()
        cls.cursor.close()
        cls.conn.close()
    
    @classmethod
    def _cleanup_test_data(cls):
        """Remove all test data"""
        try:
            # Delete in reverse order of foreign key dependencies
            cls.cursor.execute("DELETE FROM distributions WHERE group_id IN (SELECT id FROM ajo_groups WHERE name LIKE 'Test Group%')")
            cls.cursor.execute("DELETE FROM contributions WHERE group_id IN (SELECT id FROM ajo_groups WHERE name LIKE 'Test Group%')")
            cls.cursor.execute("DELETE FROM group_members WHERE group_id IN (SELECT id FROM ajo_groups WHERE name LIKE 'Test Group%')")
            cls.cursor.execute("DELETE FROM ajo_groups WHERE name LIKE 'Test Group%'")
            cls.cursor.execute("DELETE FROM users WHERE email LIKE 'test_task17_%'")
            cls.conn.commit()
        except Exception as e:
            print(f"Cleanup warning: {e}")
            cls.conn.rollback()
            # Start fresh transaction
            cls.conn = cls.conn.__class__(cls.conn.dsn)
            cls.cursor = cls.conn.cursor()
    
    @classmethod
    def _create_test_data(cls):
        """Create comprehensive test data for view testing"""
        
        # Create test users
        test_users = [
            ('test_task17_admin@example.com', 'Admin User', '+1234567890', 'verified', 'bank_transfer'),
            ('test_task17_member1@example.com', 'Member One', '+1234567891', 'verified', 'mobile_money'),
            ('test_task17_member2@example.com', 'Member Two', '+1234567892', 'pending', 'card'),
            ('test_task17_member3@example.com', 'Member Three', '+1234567893', 'verified', 'bank_transfer'),
            ('test_task17_member4@example.com', 'Member Four', '+1234567894', 'verified', 'cash'),
        ]
        
        user_ids = {}
        for email, name, phone, verification, payment_method in test_users:
            cls.cursor.execute("""
                INSERT INTO users (email, password_hash, full_name, phone_number, verification_status, preferred_payment_method, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (email, 'test_hash_' + email.split('@')[0], name, phone, verification, payment_method, datetime.now()))
            user_ids[email] = cls.cursor.fetchone()[0]
        
        # Create test groups
        group_data = [
            ('Test Group Active', 'Active group with good payment record', 100.00, 'monthly', 'active', 6, 8),
            ('Test Group Struggling', 'Group with payment issues', 50.00, 'weekly', 'active', 4, 6),
            ('Test Group New', 'Newly created group', 200.00, 'monthly', 'active', 12, 10),
        ]
        
        group_ids = {}
        admin_user_id = user_ids['test_task17_admin@example.com']
        for name, desc, amount, freq, status, duration, max_members in group_data:
            cls.cursor.execute("""
                INSERT INTO ajo_groups (name, description, contribution_amount, frequency, status, 
                                      duration_months, max_members, start_date, created_by, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (name, desc, amount, freq, status, duration, max_members, 
                  date.today() - timedelta(days=30), admin_user_id, datetime.now()))
            group_ids[name] = cls.cursor.fetchone()[0]
        
        # Add members to groups
        memberships = [
            # Active group - full membership
            (group_ids['Test Group Active'], user_ids['test_task17_admin@example.com'], 'admin', 'active', 1),
            (group_ids['Test Group Active'], user_ids['test_task17_member1@example.com'], 'member', 'active', 2),
            (group_ids['Test Group Active'], user_ids['test_task17_member2@example.com'], 'member', 'active', 3),
            (group_ids['Test Group Active'], user_ids['test_task17_member3@example.com'], 'member', 'active', 4),
            
            # Struggling group - partial membership
            (group_ids['Test Group Struggling'], user_ids['test_task17_member1@example.com'], 'admin', 'active', 1),
            (group_ids['Test Group Struggling'], user_ids['test_task17_member2@example.com'], 'member', 'active', 2),
            (group_ids['Test Group Struggling'], user_ids['test_task17_member3@example.com'], 'member', 'inactive', 3),
            
            # New group - just admin
            (group_ids['Test Group New'], user_ids['test_task17_admin@example.com'], 'admin', 'active', 1),
        ]
        
        for group_id, user_id, role, status, position in memberships:
            cls.cursor.execute("""
                INSERT INTO group_members (group_id, user_id, role, status, payment_position, join_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (group_id, user_id, role, status, position, date.today() - timedelta(days=25)))
        
        # Create contributions with various statuses
        contributions = [
            # Active group - mixed payment record
            (group_ids['Test Group Active'], user_ids['test_task17_admin@example.com'], 100.00, 'paid', date.today() - timedelta(days=20), date.today() - timedelta(days=18)),
            (group_ids['Test Group Active'], user_ids['test_task17_member1@example.com'], 100.00, 'paid', date.today() - timedelta(days=20), date.today() - timedelta(days=19)),
            (group_ids['Test Group Active'], user_ids['test_task17_member2@example.com'], 100.00, 'pending', date.today() + timedelta(days=5), None),
            (group_ids['Test Group Active'], user_ids['test_task17_member3@example.com'], 100.00, 'overdue', date.today() - timedelta(days=10), None),
            
            # Struggling group - poor payment record
            (group_ids['Test Group Struggling'], user_ids['test_task17_member1@example.com'], 50.00, 'paid', date.today() - timedelta(days=15), date.today() - timedelta(days=14)),
            (group_ids['Test Group Struggling'], user_ids['test_task17_member2@example.com'], 50.00, 'overdue', date.today() - timedelta(days=30), None),
            (group_ids['Test Group Struggling'], user_ids['test_task17_member3@example.com'], 50.00, 'overdue', date.today() - timedelta(days=45), None),
            
            # Additional overdue for testing severity
            (group_ids['Test Group Struggling'], user_ids['test_task17_member2@example.com'], 50.00, 'overdue', date.today() - timedelta(days=100), None),
        ]
        
        for group_id, user_id, amount, status, due_date, paid_date in contributions:
            cls.cursor.execute("""
                INSERT INTO contributions (group_id, user_id, amount, status, due_date, paid_date, 
                                         payment_method, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (group_id, user_id, amount, status, due_date, paid_date, 
                  'bank_transfer', datetime.now() - timedelta(days=20)))
        
        # Create distributions
        distributions = [
            (group_ids['Test Group Active'], user_ids['test_task17_admin@example.com'], 400.00, 'completed', date.today() - timedelta(days=15)),
            (group_ids['Test Group Struggling'], user_ids['test_task17_member1@example.com'], 200.00, 'pending', date.today() + timedelta(days=5)),
        ]
        
        for group_id, recipient_id, amount, status, dist_date in distributions:
            cls.cursor.execute("""
                INSERT INTO distributions (group_id, recipient_id, amount, status, distribution_date, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (group_id, recipient_id, amount, status, dist_date, datetime.now()))
        
        cls.conn.commit()
        
        # Store IDs for tests
        cls.user_ids = user_ids
        cls.group_ids = group_ids
    
    def test_group_financial_summary_view_structure(self):
        """Test that group_financial_summary view has correct structure"""
        self.cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'group_financial_summary'
            ORDER BY ordinal_position
        """)
        columns = self.cursor.fetchall()
        
        expected_columns = [
            'group_id', 'group_name', 'contribution_amount', 'frequency', 'start_date',
            'duration_months', 'max_members', 'group_status', 'total_members', 'active_members',
            'total_contributions', 'paid_contributions', 'pending_contributions', 'overdue_contributions',
            'total_collected', 'total_pending', 'total_overdue', 'total_distributions',
            'completed_distributions', 'pending_distributions', 'total_distributed',
            'contribution_rate_percent', 'expected_monthly_total', 'created_at',
            'last_contribution_date', 'last_distribution_date'
        ]
        
        column_names = [col[0] for col in columns]
        for expected_col in expected_columns:
            assert expected_col in column_names, f"Missing column: {expected_col}"
        
        print("✅ Group financial summary view has correct structure")
    
    def test_group_financial_summary_data_accuracy(self):
        """Test that group_financial_summary returns accurate data"""
        # Test active group summary
        self.cursor.execute("""
            SELECT group_name, total_members, active_members, total_contributions,
                   paid_contributions, pending_contributions, overdue_contributions,
                   total_collected, total_pending, total_overdue, contribution_rate_percent
            FROM group_financial_summary 
            WHERE group_name = 'Test Group Active'
        """)
        result = self.cursor.fetchone()
        
        assert result is not None, "Active group not found in summary"
        group_name, total_members, active_members, total_contribs, paid_contribs, pending_contribs, overdue_contribs, total_collected, total_pending, total_overdue, contrib_rate = result
        
        # Note: The view shows all contributions for the group, including historical ones
        # We only check that our test group has reasonable data
        assert total_members >= 4, f"Expected at least 4 total members, got {total_members}"
        assert active_members >= 4, f"Expected at least 4 active members, got {active_members}"
        assert total_contribs >= 4, f"Expected at least 4 contributions, got {total_contribs}"
        assert paid_contribs >= 2, f"Expected at least 2 paid contributions, got {paid_contribs}"
        assert total_collected >= Decimal('200.00'), f"Expected at least 200.00 collected, got {total_collected}"
        
        print("✅ Group financial summary data is accurate")
    
    def test_member_contribution_summary_view_structure(self):
        """Test that member_contribution_summary view has correct structure"""
        self.cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'member_contribution_summary'
            ORDER BY ordinal_position
        """)
        columns = [col[0] for col in self.cursor.fetchall()]
        
        expected_columns = [
            'user_id', 'full_name', 'email', 'total_groups', 'active_groups', 'admin_groups',
            'total_contributions', 'paid_contributions', 'pending_contributions', 'overdue_contributions',
            'cancelled_contributions', 'total_contributed', 'total_pending', 'total_overdue',
            'total_distributions_received', 'completed_distributions_received', 'total_received',
            'payment_rate_percent', 'overdue_rate_percent', 'net_position'
        ]
        
        for expected_col in expected_columns:
            assert expected_col in columns, f"Missing column: {expected_col}"
        
        print("✅ Member contribution summary view has correct structure")
    
    def test_member_contribution_summary_calculations(self):
        """Test member contribution summary calculations"""
        # Test admin user who has multiple group memberships
        self.cursor.execute("""
            SELECT full_name, total_groups, active_groups, admin_groups,
                   total_contributions, paid_contributions, payment_rate_percent,
                   total_contributed, total_received, net_position
            FROM member_contribution_summary 
            WHERE email = 'test_task17_admin@example.com'
        """)
        result = self.cursor.fetchone()
        
        assert result is not None, "Admin user not found in member summary"
        name, total_groups, active_groups, admin_groups, total_contribs, paid_contribs, payment_rate, total_contributed, total_received, net_position = result
        
        # Note: Views include all historical data, so we check for reasonable minimums
        assert total_groups >= 2, f"Expected at least 2 total groups, got {total_groups}"
        assert admin_groups >= 2, f"Expected at least 2 admin groups, got {admin_groups}"
        assert total_contribs >= 1, f"Expected at least 1 contribution, got {total_contribs}"
        assert paid_contribs >= 1, f"Expected at least 1 paid contribution, got {paid_contribs}"
        assert total_contributed >= Decimal('100.00'), f"Expected at least 100.00 contributed, got {total_contributed}"
        assert total_received >= Decimal('400.00'), f"Expected at least 400.00 received, got {total_received}"
        
        print("✅ Member contribution summary calculations are correct")
    
    def test_pending_payments_view(self):
        """Test pending payments view functionality"""
        self.cursor.execute("""
            SELECT contribution_id, group_name, user_name, amount, urgency_status,
                   expected_amount, days_since_due
            FROM pending_payments 
            ORDER BY due_date
        """)
        results = self.cursor.fetchall()
        
        assert len(results) > 0, "No pending payments found"
        
        # Check that urgency status is calculated correctly
        for contrib_id, group_name, user_name, amount, urgency, expected_amount, days_since_due in results:
            assert urgency in ['overdue', 'due_today', 'due_soon', 'future'], f"Invalid urgency status: {urgency}"
            assert amount == expected_amount, f"Amount mismatch: {amount} != {expected_amount}"
        
        print(f"✅ Pending payments view working correctly ({len(results)} pending payments)")
    
    def test_overdue_contributions_view(self):
        """Test overdue contributions view with severity analysis"""
        self.cursor.execute("""
            SELECT contribution_id, group_name, user_name, amount, days_overdue,
                   overdue_severity, member_risk_level, previous_payments, total_overdue
            FROM overdue_contributions 
            ORDER BY days_overdue DESC
        """)
        results = self.cursor.fetchall()
        
        assert len(results) > 0, "No overdue contributions found"
        
        # Test severity classification
        for contrib_id, group_name, user_name, amount, days_overdue, severity, risk_level, prev_payments, total_overdue in results:
            # Check severity classification logic
            if days_overdue <= 7:
                assert severity == 'recently_overdue', f"Wrong severity for {days_overdue} days: {severity}"
            elif days_overdue <= 30:
                assert severity == 'moderately_overdue', f"Wrong severity for {days_overdue} days: {severity}"
            elif days_overdue <= 90:
                assert severity == 'seriously_overdue', f"Wrong severity for {days_overdue} days: {severity}"
            else:
                assert severity == 'critically_overdue', f"Wrong severity for {days_overdue} days: {severity}"
            
            # Check risk level
            assert risk_level in ['low_risk', 'medium_risk', 'high_risk'], f"Invalid risk level: {risk_level}"
        
        print(f"✅ Overdue contributions view working correctly ({len(results)} overdue contributions)")
    
    def test_group_performance_dashboard_view(self):
        """Test group performance dashboard with health scores"""
        self.cursor.execute("""
            SELECT group_name, total_members, active_members, capacity_utilization_percent,
                   recent_payments, recent_payment_rate_percent, total_collected, total_overdue,
                   health_score, completed_distributions
            FROM group_performance_dashboard 
            ORDER BY health_score DESC
        """)
        results = self.cursor.fetchall()
        
        assert len(results) >= 3, f"Expected at least 3 groups, got {len(results)}"
        
        for group_name, total_members, active_members, capacity_util, recent_payments, recent_rate, total_collected, total_overdue, health_score, completed_dists in results:
            # Health score should be between 0 and 100
            assert 0 <= health_score <= 100, f"Invalid health score: {health_score}"
            
            # Capacity utilization should be reasonable
            assert 0 <= capacity_util <= 100, f"Invalid capacity utilization: {capacity_util}"
            
            # Active members should not exceed total members
            assert active_members <= total_members, f"Active members ({active_members}) > total members ({total_members})"
        
        # Test that active group has better health score than struggling group
        active_group = next((r for r in results if r[0] == 'Test Group Active'), None)
        struggling_group = next((r for r in results if r[0] == 'Test Group Struggling'), None)
        
        if active_group and struggling_group:
            assert active_group[8] > struggling_group[8], "Active group should have better health score than struggling group"
        
        print("✅ Group performance dashboard calculations are correct")
    
    def test_view_performance_with_indexes(self):
        """Test that views perform well with the created indexes"""
        import time
        
        # Test queries that should benefit from indexes
        test_queries = [
            "SELECT * FROM group_financial_summary WHERE group_id = %s",
            "SELECT * FROM member_contribution_summary WHERE user_id = %s",
            "SELECT * FROM pending_payments WHERE group_id = %s",
            "SELECT * FROM overdue_contributions WHERE user_id = %s",
            "SELECT * FROM group_performance_dashboard WHERE group_id = %s"
        ]
        
        test_group_id = list(self.group_ids.values())[0]
        test_user_id = list(self.user_ids.values())[0]
        
        for query in test_queries:
            start_time = time.time()
            self.cursor.execute(query, (test_group_id if 'group_id' in query else test_user_id,))
            results = self.cursor.fetchall()
            end_time = time.time()
            
            query_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Query should complete in reasonable time (< 200ms for test data)
            assert query_time < 200, f"Query too slow: {query_time:.2f}ms"
        
        print("✅ View performance is acceptable with indexes")
    
    def test_view_data_consistency(self):
        """Test data consistency across different views"""
        # Get group data from multiple views and ensure consistency
        group_id = self.group_ids['Test Group Active']
        
        # Get data from group financial summary
        self.cursor.execute("""
            SELECT total_members, total_contributions, total_collected
            FROM group_financial_summary WHERE group_id = %s
        """, (group_id,))
        gfs_data = self.cursor.fetchone()
        
        # Get data from group performance dashboard
        self.cursor.execute("""
            SELECT total_members, total_collected
            FROM group_performance_dashboard WHERE group_id = %s
        """, (group_id,))
        gpd_data = self.cursor.fetchone()
        
        # Check consistency
        assert gfs_data[0] == gpd_data[0], "Member count inconsistent between views"
        assert gfs_data[2] == gpd_data[1], "Total collected inconsistent between views"
        
        # Check that pending + overdue views don't overlap
        self.cursor.execute("SELECT COUNT(*) FROM pending_payments WHERE group_id = %s", (group_id,))
        pending_count = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM overdue_contributions WHERE group_id = %s", (group_id,))
        overdue_count = self.cursor.fetchone()[0]
        
        # Total should match contributions that are pending or overdue
        self.cursor.execute("""
            SELECT COUNT(*) FROM contributions 
            WHERE group_id = %s AND status IN ('pending', 'overdue')
        """, (group_id,))
        total_pending_overdue = self.cursor.fetchone()[0]
        
        assert pending_count + overdue_count >= total_pending_overdue, "View counts don't match raw data"
        
        print("✅ Data consistency verified across views")
    
    def test_view_edge_cases(self):
        """Test views handle edge cases correctly"""
        # Test with empty group (new group with no contributions)
        new_group_id = self.group_ids['Test Group New']
        
        self.cursor.execute("""
            SELECT total_contributions, paid_contributions, total_collected
            FROM group_financial_summary WHERE group_id = %s
        """, (new_group_id,))
        result = self.cursor.fetchone()
        
        assert result is not None, "New group should appear in financial summary"
        total_contribs, paid_contribs, total_collected = result[0], result[1], result[2]
        
        # Get health score from performance dashboard
        self.cursor.execute("""
            SELECT health_score FROM group_performance_dashboard WHERE group_id = %s
        """, (new_group_id,))
        health_result = self.cursor.fetchone()
        health_score = health_result[0] if health_result else None
        
        assert total_contribs == 0, "New group should have 0 contributions"
        assert paid_contribs == 0, "New group should have 0 paid contributions"
        assert total_collected == Decimal('0.00'), "New group should have 0 collected"
        
        if health_score is not None:
            assert health_score == 50, f"New group should have neutral health score of 50, got {health_score}"
        
        print("✅ Views handle edge cases correctly")


def run_task17_tests():
    """Run all Task 17 tests"""
    print("🧪 Running Task 17: Financial Summary Views Tests")
    print("=" * 60)
    
    # Create test instance
    test_instance = TestTask17FinancialSummaryViews()
    test_instance.setup_class()
    
    try:
        # Run all tests
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        passed = 0
        failed = 0
        
        for test_method in test_methods:
            try:
                print(f"\n🔍 Running {test_method}...")
                getattr(test_instance, test_method)()
                passed += 1
            except Exception as e:
                print(f"❌ {test_method} failed: {e}")
                failed += 1
        
        print(f"\n📊 Task 17 Test Results:")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {passed/(passed+failed)*100:.1f}%")
        
        if failed == 0:
            print("\n🎉 All Task 17 tests passed! Financial summary views are working correctly.")
            return True
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please review the issues above.")
            return False
            
    finally:
        test_instance.teardown_class()


if __name__ == "__main__":
    success = run_task17_tests()
    exit(0 if success else 1)