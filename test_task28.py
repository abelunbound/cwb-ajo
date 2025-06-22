"""
Test Suite for Task 28: Build Group Discovery Interface

This test suite covers:
- Group discovery service functionality
- UI component creation and rendering
- Search and filtering capabilities
- Pagination functionality
- Group detail modal operations
- Join request processing
- Error handling and edge cases

Run with: python test_task28.py
"""

import sys
import os
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from datetime import datetime, date

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def pytest_fail(message):
    """Simple replacement for pytest.fail"""
    raise AssertionError(message)

class TestTask28GroupDiscoveryService:
    """Test the group discovery service functionality."""
    
    def test_service_file_exists(self):
        """Test that the group discovery service file exists."""
        service_path = os.path.join(os.path.dirname(__file__), 'services', 'group_discovery_service.py')
        assert os.path.exists(service_path), "services/group_discovery_service.py should exist"
    
    def test_service_imports(self):
        """Test that the service can be imported successfully."""
        try:
            from services import group_discovery_service
            assert hasattr(group_discovery_service, 'get_discoverable_groups')
            assert hasattr(group_discovery_service, 'search_groups')
            assert hasattr(group_discovery_service, 'get_group_details_for_discovery')
            assert hasattr(group_discovery_service, 'can_user_join_group')
            assert hasattr(group_discovery_service, 'get_filter_options')
        except ImportError as e:
            pytest_fail(f"Failed to import group discovery service: {e}")
    
    @patch('services.group_discovery_service.get_ajo_db_connection')
    def test_get_discoverable_groups_success(self, mock_db_conn):
        """Test successful retrieval of discoverable groups."""
        from services.group_discovery_service import get_discoverable_groups
        
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock count query result
        mock_cursor.fetchone.return_value = [2]  # total count
        
        # Mock groups query result
        mock_cursor.fetchall.return_value = [
            (1, 'Test Group 1', 'Description 1', Decimal('100'), 'monthly', 
             date(2024, 1, 1), 12, 8, 'active', datetime.now(), date(2024, 12, 31), 3, 'John Doe'),
            (2, 'Test Group 2', 'Description 2', Decimal('50'), 'weekly',
             date(2024, 2, 1), 6, 5, 'active', datetime.now(), date(2024, 8, 1), 2, 'Jane Smith')
        ]
        
        result = get_discoverable_groups(user_id=1, page=1, per_page=12)
        
        assert result['success'] is True
        assert len(result['groups']) == 2
        assert result['total_count'] == 2
        assert result['page'] == 1
        assert result['per_page'] == 12
        assert result['total_pages'] == 1
        
        # Check group data structure
        group1 = result['groups'][0]
        assert group1['id'] == 1
        assert group1['name'] == 'Test Group 1'
        assert group1['contribution_amount'] == Decimal('100')
        assert group1['current_members'] == 3
        assert group1['spots_available'] == 5  # max_members - current_members
        assert group1['is_full'] is False
    
    @patch('services.group_discovery_service.get_ajo_db_connection')
    def test_search_groups_with_query(self, mock_db_conn):
        """Test searching groups with search query."""
        from services.group_discovery_service import search_groups
        
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = [1]  # count
        mock_cursor.fetchall.return_value = [
            (1, 'Savings Group', 'Monthly savings', Decimal('100'), 'monthly',
             date(2024, 1, 1), 12, 8, 'active', datetime.now(), date(2024, 12, 31), 3, 'John Doe')
        ]
        
        result = search_groups(user_id=1, query="savings", filters={}, page=1, per_page=12)
        
        assert result['success'] is True
        assert len(result['groups']) == 1
        assert result['query'] == "savings"
        assert 'savings' in result['groups'][0]['name'].lower()
    
    @patch('services.group_discovery_service.get_ajo_db_connection')
    def test_search_groups_with_filters(self, mock_db_conn):
        """Test searching groups with filters."""
        from services.group_discovery_service import search_groups
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        mock_cursor.fetchone.return_value = [1]
        mock_cursor.fetchall.return_value = [
            (1, 'Test Group', 'Description', Decimal('100'), 'monthly',
             date(2024, 1, 1), 12, 8, 'active', datetime.now(), date(2024, 12, 31), 3, 'John Doe')
        ]
        
        filters = {
            'contribution_amount': [100],
            'frequency': ['monthly'],
            'min_spots': 2
        }
        
        result = search_groups(user_id=1, query="", filters=filters, page=1, per_page=12)
        
        assert result['success'] is True
        assert result['filters'] == filters
    
    @patch('services.group_discovery_service.get_ajo_db_connection')
    def test_get_group_details_for_discovery(self, mock_db_conn):
        """Test getting detailed group information for discovery."""
        from services.group_discovery_service import get_group_details_for_discovery
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock membership check (user not a member)
        mock_cursor.fetchone.side_effect = [
            None,  # Not a member
            (1, 'Test Group', 'Description', Decimal('100'), 'monthly',
             date(2024, 1, 1), 12, 8, 'active', datetime.now(), date(2024, 12, 31), 
             'ABC12345', 3, 'John Doe', 'john@example.com')  # Group details
        ]
        
        # Mock members query
        mock_cursor.fetchall.return_value = [
            ('admin', 1, 'John Doe'),
            ('member', 2, 'Jane Smith'),
            ('member', 3, 'Bob Wilson')
        ]
        
        result = get_group_details_for_discovery(group_id=1, user_id=2)
        
        assert result is not None
        assert result['id'] == 1
        assert result['name'] == 'Test Group'
        assert result['current_members'] == 3
        assert result['spots_available'] == 5
        assert len(result['members']) == 3
        assert result['members'][0]['role'] == 'admin'
    
    @patch('services.group_discovery_service.get_ajo_db_connection')
    def test_can_user_join_group_success(self, mock_db_conn):
        """Test checking if user can join a group - success case."""
        from services.group_discovery_service import can_user_join_group
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock responses: group exists, user not member, group not full
        mock_cursor.fetchone.side_effect = [
            (1, 8, 'active'),  # Group details
            None,  # User not a member
            [3]  # Current member count
        ]
        
        result = can_user_join_group(group_id=1, user_id=2)
        
        assert result['can_join'] is True
        assert result['spots_available'] == 5
    
    @patch('services.group_discovery_service.get_ajo_db_connection')
    def test_can_user_join_group_already_member(self, mock_db_conn):
        """Test checking if user can join a group - already a member."""
        from services.group_discovery_service import can_user_join_group
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock responses: group exists, user is already a member
        mock_cursor.fetchone.side_effect = [
            (1, 8, 'active'),  # Group details
            (1,)  # User is a member
        ]
        
        result = can_user_join_group(group_id=1, user_id=2)
        
        assert result['can_join'] is False
        assert result['reason'] == 'Already a member of this group'
    
    @patch('services.group_discovery_service.get_ajo_db_connection')
    def test_can_user_join_group_full(self, mock_db_conn):
        """Test checking if user can join a group - group is full."""
        from services.group_discovery_service import can_user_join_group
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock responses: group exists, user not member, group is full
        mock_cursor.fetchone.side_effect = [
            (1, 5, 'active'),  # Group details (max 5 members)
            None,  # User not a member
            [5]  # Current member count (full)
        ]
        
        result = can_user_join_group(group_id=1, user_id=2)
        
        assert result['can_join'] is False
        assert result['reason'] == 'Group is full'
    
    @patch('services.group_discovery_service.get_ajo_db_connection')
    def test_get_filter_options(self, mock_db_conn):
        """Test getting filter options from database."""
        from services.group_discovery_service import get_filter_options
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock filter options from database
        mock_cursor.fetchall.side_effect = [
            [(Decimal('50'),), (Decimal('100'),), (Decimal('500'),)],  # Amounts
            [('weekly',), ('monthly',)]  # Frequencies
        ]
        
        result = get_filter_options()
        
        assert 'contribution_amounts' in result
        assert 'frequencies' in result
        assert Decimal('50') in result['contribution_amounts']
        assert 'weekly' in result['frequencies']


class TestTask28UIComponents:
    """Test the UI components for group discovery."""
    
    def test_discovery_page_exists(self):
        """Test that the discovery page file exists."""
        page_path = os.path.join(os.path.dirname(__file__), 'pages', 'discover_groups.py')
        assert os.path.exists(page_path), "pages/discover_groups.py should exist"
    
    def test_discovery_component_exists(self):
        """Test that the discovery component file exists."""
        component_path = os.path.join(os.path.dirname(__file__), 'components', 'group_discovery.py')
        assert os.path.exists(component_path), "components/group_discovery.py should exist"
    
    def test_discovery_page_imports(self):
        """Test that the discovery page can be imported."""
        try:
            from pages import discover_groups
            assert hasattr(discover_groups, 'layout')
        except ImportError as e:
            pytest_fail(f"Failed to import discover groups page: {e}")
    
    def test_discovery_component_imports(self):
        """Test that the discovery component functions can be imported."""
        try:
            from components import group_discovery
            assert hasattr(group_discovery, 'create_discovery_section')
            assert hasattr(group_discovery, 'create_group_discovery_card')
            assert hasattr(group_discovery, 'create_group_grid')
            assert hasattr(group_discovery, 'create_group_detail_modal')
            assert hasattr(group_discovery, 'create_empty_state')
            assert hasattr(group_discovery, 'create_loading_state')
            assert hasattr(group_discovery, 'create_error_state')
        except ImportError as e:
            pytest_fail(f"Failed to import group discovery component: {e}")
    
    def test_create_group_discovery_card(self):
        """Test creating a group discovery card."""
        try:
            from components.group_discovery import create_group_discovery_card
            
            group_data = {
                'id': 1,
                'name': 'Test Group',
                'description': 'Test description',
                'contribution_amount': Decimal('100'),
                'frequency': 'monthly',
                'current_members': 3,
                'max_members': 8,
                'duration_months': 12,
                'creator_name': 'John Doe',
                'spots_available': 5,
                'is_full': False,
                'start_date': date(2024, 1, 1)
            }
            
            card = create_group_discovery_card(group_data)
            
            # Card should be a Dash Bootstrap component
            assert hasattr(card, 'children')
            assert card.className == "h-100 shadow-sm group-discovery-card"
        except Exception as e:
            pytest_fail(f"Failed to create group discovery card: {e}")
    
    def test_create_group_grid_with_groups(self):
        """Test creating a group grid with groups."""
        try:
            from components.group_discovery import create_group_grid
            
            groups = [
                {
                    'id': 1,
                    'name': 'Group 1',
                    'description': 'Description 1',
                    'contribution_amount': Decimal('100'),
                    'frequency': 'monthly',
                    'current_members': 3,
                    'max_members': 8,
                    'duration_months': 12,
                    'creator_name': 'John Doe',
                    'spots_available': 5,
                    'is_full': False
                },
                {
                    'id': 2,
                    'name': 'Group 2',
                    'description': 'Description 2',
                    'contribution_amount': Decimal('50'),
                    'frequency': 'weekly',
                    'current_members': 2,
                    'max_members': 5,
                    'duration_months': 6,
                    'creator_name': 'Jane Smith',
                    'spots_available': 3,
                    'is_full': False
                }
            ]
            
            grid = create_group_grid(groups)
            
            assert hasattr(grid, 'children')
            assert grid.className == "row"
            assert len(grid.children) == 2  # Two group cards
        except Exception as e:
            pytest_fail(f"Failed to create group grid: {e}")
    
    def test_create_group_grid_empty(self):
        """Test creating a group grid with no groups."""
        try:
            from components.group_discovery import create_group_grid
            
            grid = create_group_grid([])
            
            # Should return empty state
            assert hasattr(grid, 'children')
            # Check for empty state indicators
            assert any("No Groups Found" in str(child) for child in grid.children if hasattr(child, 'children'))
        except Exception as e:
            pytest_fail(f"Failed to create empty group grid: {e}")
    
    def test_create_loading_state(self):
        """Test creating loading state component."""
        try:
            from components.group_discovery import create_loading_state
            
            loading = create_loading_state()
            
            assert hasattr(loading, 'children')
            assert loading.className == "text-center py-5"
        except Exception as e:
            pytest_fail(f"Failed to create loading state: {e}")
    
    def test_create_error_state(self):
        """Test creating error state component."""
        try:
            from components.group_discovery import create_error_state
            
            error = create_error_state("Test error message")
            
            assert hasattr(error, 'children')
            assert error.className == "text-center py-5"
        except Exception as e:
            pytest_fail(f"Failed to create error state: {e}")
    
    def test_create_group_detail_content(self):
        """Test creating group detail content."""
        try:
            from components.group_discovery import create_group_detail_content
            
            group_data = {
                'id': 1,
                'name': 'Test Group',
                'description': 'Detailed description',
                'contribution_amount': Decimal('100'),
                'frequency': 'monthly',
                'duration_months': 12,
                'current_members': 3,
                'max_members': 8,
                'spots_available': 5,
                'is_full': False,
                'status': 'active',
                'creator_name': 'John Doe',
                'start_date': date(2024, 1, 1),
                'end_date': date(2024, 12, 31),
                'members': [
                    {'role': 'admin', 'payment_position': 1, 'name': 'John Doe'},
                    {'role': 'member', 'payment_position': 2, 'name': 'Jane Smith'}
                ]
            }
            
            content = create_group_detail_content(group_data)
            
            assert hasattr(content, 'children')
            # Should contain group information
            content_str = str(content)
            assert 'Test Group' in content_str or 'Detailed description' in content_str
        except Exception as e:
            pytest_fail(f"Failed to create group detail content: {e}")


class TestTask28Integration:
    """Test integration aspects of Task 28."""
    
    def test_groups_page_navigation_added(self):
        """Test that navigation to discover groups was added to groups page."""
        try:
            from pages import groups
            
            # Check that the page layout includes discover groups navigation
            layout_str = str(groups.layout)
            assert 'discover-groups' in layout_str or 'Discover Groups' in layout_str
        except Exception as e:
            pytest_fail(f"Failed to verify groups page navigation: {e}")
    
    def test_callbacks_discovery_functions_exist(self):
        """Test that discovery callbacks exist in callbacks.py."""
        try:
            # Read callbacks file to check for discovery functions
            callbacks_path = os.path.join(os.path.dirname(__file__), 'callbacks.py')
            with open(callbacks_path, 'r') as f:
                content = f.read()
            
            # Check for key discovery callback functions
            assert 'update_group_discovery' in content
            assert 'handle_group_detail_modal' in content
            assert 'handle_join_request_modal' in content
            assert 'clear_discovery_filters' in content
            
            # Check for discovery-related IDs
            assert 'discovery-content' in content
            assert 'discovery-search-btn' in content
            assert 'discovery-pagination' in content
        except Exception as e:
            pytest_fail(f"Failed to verify discovery callbacks: {e}")
    
    @patch('services.group_discovery_service.get_ajo_db_connection')
    def test_database_integration_user_exclusion(self, mock_db_conn):
        """Test that the service properly excludes groups user is already in."""
        from services.group_discovery_service import get_discoverable_groups
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock that user is in one group, so should see others
        mock_cursor.fetchone.return_value = [1]  # 1 discoverable group
        mock_cursor.fetchall.return_value = [
            (2, 'Available Group', 'Description', Decimal('100'), 'monthly',
             date(2024, 1, 1), 12, 8, 'active', datetime.now(), date(2024, 12, 31), 3, 'John Doe')
        ]
        
        result = get_discoverable_groups(user_id=1, page=1, per_page=12)
        
        assert result['success'] is True
        assert len(result['groups']) == 1
        
        # Verify SQL excludes user's groups
        calls = mock_cursor.execute.call_args_list
        sql_calls = [call[0][0] for call in calls]
        
        # Should have exclusion clause for user's groups
        assert any('NOT IN' in sql and 'group_members' in sql for sql in sql_calls)


class TestTask28ErrorHandling:
    """Test error handling in Task 28 implementation."""
    
    @patch('services.group_discovery_service.get_ajo_db_connection')
    def test_database_connection_failure(self, mock_db_conn):
        """Test handling of database connection failure."""
        from services.group_discovery_service import get_discoverable_groups
        
        mock_db_conn.return_value = None  # Simulate connection failure
        
        result = get_discoverable_groups(user_id=1)
        
        assert result['success'] is False
        assert 'Database connection failed' in result['error']
    
    @patch('services.group_discovery_service.get_ajo_db_connection')
    def test_database_error_handling(self, mock_db_conn):
        """Test handling of database errors."""
        from services.group_discovery_service import search_groups
        import psycopg2
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock database error
        mock_cursor.execute.side_effect = psycopg2.Error("Database error")
        
        result = search_groups(user_id=1, query="test")
        
        assert result['success'] is False
        assert 'Database error' in result['error']
    
    def test_group_not_found_handling(self):
        """Test handling when group is not found."""
        try:
            from services.group_discovery_service import get_group_details_for_discovery
            
            with patch('services.group_discovery_service.get_ajo_db_connection') as mock_db_conn:
                mock_conn = MagicMock()
                mock_cursor = MagicMock()
                mock_db_conn.return_value = mock_conn
                mock_conn.cursor.return_value = mock_cursor
                
                # Mock group not found
                mock_cursor.fetchone.side_effect = [None, None]  # Not a member, group not found
                
                result = get_group_details_for_discovery(group_id=999, user_id=1)
                
                assert result is None
        except Exception as e:
            pytest_fail(f"Error handling test failed: {e}")


def run_task28_tests():
    """Run all Task 28 tests and return results."""
    print("=" * 80)
    print("TASK 28: BUILD GROUP DISCOVERY INTERFACE - TEST RESULTS")
    print("=" * 80)
    
    # Test categories
    test_categories = [
        ("Service Layer Tests", TestTask28GroupDiscoveryService),
        ("UI Component Tests", TestTask28UIComponents),
        ("Integration Tests", TestTask28Integration),
        ("Error Handling Tests", TestTask28ErrorHandling),
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for category_name, test_class in test_categories:
        print(f"\n{category_name}:")
        print("-" * 50)
        
        # Get all test methods
        test_methods = [method for method in dir(test_class) if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            try:
                # Create instance and run test
                test_instance = test_class()
                getattr(test_instance, test_method)()
                print(f"✅ {test_method}")
                passed_tests += 1
            except Exception as e:
                print(f"❌ {test_method}: {str(e)}")
                failed_tests.append(f"{test_class.__name__}.{test_method}: {str(e)}")
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests:
        print(f"\nFailed Tests:")
        for failure in failed_tests:
            print(f"  - {failure}")
    
    return {
        'total': total_tests,
        'passed': passed_tests,
        'failed': len(failed_tests),
        'success_rate': (passed_tests/total_tests)*100,
        'failures': failed_tests
    }


if __name__ == "__main__":
    results = run_task28_tests()
    
    # Exit with error code if tests failed
    if results['failed'] > 0:
        sys.exit(1)
    else:
        print(f"\n🎉 All {results['total']} tests passed!")
        sys.exit(0)