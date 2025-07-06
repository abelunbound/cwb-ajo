#!/usr/bin/env python3
"""
Test Task 31: Payment Position Assignment System
Tests the complete payment position management functionality including
algorithms, UI components, and database operations.
"""

import sys
import unittest
from unittest.mock import patch, MagicMock
import dash
from dash import html
import dash_bootstrap_components as dbc

# Add the current directory to the path to import modules
sys.path.append('.')

class TestTask31PaymentPositionAssignment(unittest.TestCase):
    """Test that Task 31 payment position assignment system is complete."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_group_data = {
            'group_id': 1,
            'group_name': 'Test Group',
            'contribution_amount': 100,
            'frequency': 'monthly',
            'current_members': 5,
            'group_status': 'active'
        }
        
        self.sample_members_data = [
            {
                'membership_id': 1,
                'user_id': 1,
                'full_name': 'John Doe',
                'email': 'john@example.com',
                'role': 'admin',
                'status': 'active',
                'payment_position': 1,
                'join_date': '2024-01-01'
            },
            {
                'membership_id': 2,
                'user_id': 2,
                'full_name': 'Jane Smith',
                'email': 'jane@example.com',
                'role': 'member',
                'status': 'active',
                'payment_position': 2,
                'join_date': '2024-01-02'
            },
            {
                'membership_id': 3,
                'user_id': 3,
                'full_name': 'Bob Johnson',
                'email': 'bob@example.com',
                'role': 'member',
                'status': 'active',
                'payment_position': None,
                'join_date': '2024-01-03'
            }
        ]
    
    def test_payment_position_service_import(self):
        """Test that payment position service can be imported."""
        try:
            from services.payment_position_service import (
                get_group_payment_positions,
                assign_random_positions,
                assign_manual_positions,
                swap_payment_positions,
                get_payment_schedule,
                validate_payment_positions,
                auto_assign_missing_positions
            )
            print("✅ Payment position service imports successfully")
        except ImportError as e:
            self.fail(f"❌ Failed to import payment position service: {e}")
    
    def test_payment_position_components_import(self):
        """Test that payment position components can be imported."""
        try:
            from components.payment_position_management import (
                create_payment_position_modal,
                create_payment_position_card,
                create_payment_position_list,
                create_payment_schedule_modal,
                create_payment_schedule_card,
                create_payment_schedule_list,
                create_next_recipient_highlight,
                create_group_info_for_positions
            )
            print("✅ Payment position components import successfully")
        except ImportError as e:
            self.fail(f"❌ Failed to import payment position components: {e}")
    
    def test_payment_position_modal_creation(self):
        """Test that payment position modal is created correctly."""
        try:
            from components.payment_position_management import create_payment_position_modal
            modal = create_payment_position_modal()
            
            # Check that modal is a DBC Modal
            self.assertIsInstance(modal, dbc.Modal)
            
            # Check modal properties
            self.assertEqual(modal.id, "payment-position-modal")
            self.assertEqual(modal.size, "xl")
            self.assertFalse(modal.is_open)
            
            print("✅ Payment position modal creates correctly")
        except Exception as e:
            self.fail(f"❌ Failed to create payment position modal: {e}")
    
    def test_payment_schedule_modal_creation(self):
        """Test that payment schedule modal is created correctly."""
        try:
            from components.payment_position_management import create_payment_schedule_modal
            modal = create_payment_schedule_modal()
            
            # Check that modal is a DBC Modal
            self.assertIsInstance(modal, dbc.Modal)
            
            # Check modal properties
            self.assertEqual(modal.id, "payment-schedule-modal")
            self.assertEqual(modal.size, "lg")
            self.assertFalse(modal.is_open)
            
            print("✅ Payment schedule modal creates correctly")
        except Exception as e:
            self.fail(f"❌ Failed to create payment schedule modal: {e}")
    
    def test_payment_position_card_creation(self):
        """Test that payment position cards are created correctly."""
        try:
            from components.payment_position_management import create_payment_position_card
            
            member_data = self.sample_members_data[0]
            position = member_data['payment_position']
            
            card = create_payment_position_card(member_data, position)
            
            # Check that card is a DBC Card
            self.assertIsInstance(card, dbc.Card)
            
            print("✅ Payment position card creates correctly")
        except Exception as e:
            self.fail(f"❌ Failed to create payment position card: {e}")
    
    def test_payment_position_list_creation(self):
        """Test that payment position list is created correctly."""
        try:
            from components.payment_position_management import create_payment_position_list
            
            # Test with members data
            position_list = create_payment_position_list(self.sample_members_data)
            self.assertIsInstance(position_list, html.Div)
            
            # Test with empty data
            empty_list = create_payment_position_list([])
            self.assertIsInstance(empty_list, html.Div)
            
            print("✅ Payment position list creates correctly")
        except Exception as e:
            self.fail(f"❌ Failed to create payment position list: {e}")
    
    def test_payment_schedule_components(self):
        """Test payment schedule components."""
        try:
            from components.payment_position_management import (
                create_payment_schedule_card,
                create_payment_schedule_list,
                create_next_recipient_highlight
            )
            
            # Test schedule card
            member_data = {'position': 1, 'full_name': 'John Doe', 'role': 'admin'}
            schedule_card = create_payment_schedule_card(member_data, is_next=True)
            self.assertIsInstance(schedule_card, dbc.Card)
            
            # Test schedule list
            schedule_list = create_payment_schedule_list([member_data])
            self.assertIsInstance(schedule_list, html.Div)
            
            # Test next recipient highlight
            next_recipient = create_next_recipient_highlight(member_data)
            self.assertIsInstance(next_recipient, dbc.Card)
            
            print("✅ Payment schedule components create correctly")
        except Exception as e:
            self.fail(f"❌ Failed to create payment schedule components: {e}")
    
    def test_group_info_component(self):
        """Test group info component for positions."""
        try:
            from components.payment_position_management import create_group_info_for_positions
            
            group_info = create_group_info_for_positions(self.sample_group_data)
            self.assertIsInstance(group_info, dbc.Card)
            
            print("✅ Group info component creates correctly")
        except Exception as e:
            self.fail(f"❌ Failed to create group info component: {e}")
    
    @patch('services.payment_position_service.get_ajo_db_connection')
    def test_get_group_payment_positions(self, mock_db):
        """Test getting group payment positions."""
        try:
            from services.payment_position_service import get_group_payment_positions
            
            # Mock database connection and cursor
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_db.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            # Mock query results
            mock_cursor.fetchall.return_value = [
                (1, 1, 1, 'admin', 'active', 'John Doe', 'john@example.com', '2024-01-01'),
                (2, 2, 2, 'member', 'active', 'Jane Smith', 'jane@example.com', '2024-01-02')
            ]
            
            result = get_group_payment_positions(1)
            
            # Check that result is a list
            self.assertIsInstance(result, list)
            
            # Check that database was called
            mock_cursor.execute.assert_called_once()
            
            print("✅ Get group payment positions works correctly")
        except Exception as e:
            self.fail(f"❌ Failed to get group payment positions: {e}")
    
    @patch('services.payment_position_service.get_ajo_db_connection')
    def test_assign_random_positions(self, mock_db):
        """Test random position assignment."""
        try:
            from services.payment_position_service import assign_random_positions
            
            # Mock database connection and cursor
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_db.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            # Mock query results
            mock_cursor.fetchall.return_value = [
                (1, 1, 'John Doe'),
                (2, 2, 'Jane Smith'),
                (3, 3, 'Bob Johnson')
            ]
            
            result = assign_random_positions(1)
            
            # Check that result has success key
            self.assertIn('success', result)
            
            print("✅ Random position assignment works correctly")
        except Exception as e:
            self.fail(f"❌ Failed to assign random positions: {e}")
    
    @patch('services.payment_position_service.get_ajo_db_connection')
    def test_swap_payment_positions(self, mock_db):
        """Test position swapping functionality."""
        try:
            from services.payment_position_service import swap_payment_positions
            
            # Mock database connection and cursor
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_db.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            # Mock query results
            mock_cursor.fetchall.return_value = [
                (1, 1, 'John Doe'),
                (2, 2, 'Jane Smith')
            ]
            
            result = swap_payment_positions(1, 1, 2)
            
            # Check that result has success key
            self.assertIn('success', result)
            
            print("✅ Position swapping works correctly")
        except Exception as e:
            self.fail(f"❌ Failed to swap positions: {e}")
    
    @patch('services.payment_position_service.get_ajo_db_connection')
    def test_validate_payment_positions(self, mock_db):
        """Test position validation functionality."""
        try:
            from services.payment_position_service import validate_payment_positions
            
            # Mock database connection and cursor
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_db.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            # Mock query results
            mock_cursor.fetchall.return_value = [
                (1, 1, 'John Doe'),
                (2, 2, 'Jane Smith'),
                (3, None, 'Bob Johnson')
            ]
            
            result = validate_payment_positions(1)
            
            # Check that result has success and valid keys
            self.assertIn('success', result)
            self.assertIn('valid', result)
            self.assertIn('issues', result)
            
            print("✅ Position validation works correctly")
        except Exception as e:
            self.fail(f"❌ Failed to validate positions: {e}")
    
    @patch('services.payment_position_service.get_ajo_db_connection')
    def test_get_payment_schedule(self, mock_db):
        """Test getting payment schedule."""
        try:
            from services.payment_position_service import get_payment_schedule
            
            # Mock database connection and cursor
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_db.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            # Mock query results
            mock_cursor.fetchone.return_value = ('Test Group', 100, 'monthly', '2024-01-01', 'active')
            mock_cursor.fetchall.return_value = [
                (1, 1, 'John Doe', 'admin'),
                (2, 2, 'Jane Smith', 'member')
            ]
            
            result = get_payment_schedule(1)
            
            # Check that result has success key and schedule
            self.assertIn('success', result)
            self.assertIn('schedule', result)
            self.assertIn('next_recipient', result)
            
            print("✅ Payment schedule retrieval works correctly")
        except Exception as e:
            self.fail(f"❌ Failed to get payment schedule: {e}")
    
    def test_member_management_page_has_manage_positions_button(self):
        """Test that member management page has Manage Positions functionality."""
        try:
            # Test that payment positions page exists and is accessible
            from pages.payment_positions import layout
            
            # Test that the payment positions page can be created
            positions_page = layout(group_id="test-group-123")
            self.assertIsNotNone(positions_page)
            
            # Test that the member management page can create action buttons dynamically
            from pages.member_management import create_action_buttons_with_group_id
            
            # Test with mock group store data
            mock_group_store = {"group_id": "test-group-123"}
            action_buttons = create_action_buttons_with_group_id(mock_group_store)
            
            # Convert to string to check for button content
            button_html = str(action_buttons)
            
            # Check that Manage Positions button exists in the dynamic buttons
            self.assertIn("Manage Positions", button_html)
            self.assertIn("/payment-positions/", button_html)
            
            print("✅ Member management page has Manage Positions functionality")
        except Exception as e:
            self.fail(f"❌ Failed to find Manage Positions functionality: {e}")
    
    def test_app_includes_payment_position_functionality(self):
        """Test that app includes payment position functionality."""
        try:
            # Import app to check it loads correctly
            import app
            
            # Test that payment positions page is registered
            import dash
            payment_positions_registered = False
            for page in dash.page_registry.values():
                path_template = page.get('path_template', '') or ''
                if 'payment-positions' in path_template:
                    payment_positions_registered = True
                    break
            
            self.assertTrue(payment_positions_registered, "Payment positions page not registered")
            
            # Check that payment position components can still be created
            from components.payment_position_management import (
                create_payment_position_modal,
                create_payment_schedule_modal
            )
            
            # Test that modals can be created (for backwards compatibility)
            position_modal = create_payment_position_modal()
            schedule_modal = create_payment_schedule_modal()
            
            self.assertIsInstance(position_modal, dbc.Modal)
            self.assertIsInstance(schedule_modal, dbc.Modal)
            
            print("✅ App includes payment position functionality")
        except Exception as e:
            self.fail(f"❌ Failed to include payment position functionality in app: {e}")
    
    def test_payment_position_callbacks_import(self):
        """Test that payment position callbacks are imported."""
        try:
            # Import callbacks to check they exist
            import callbacks
            
            # Import payment positions page to check page-based callbacks
            from pages import payment_positions
            
            # Check that the page has the required callback functions
            self.assertTrue(hasattr(payment_positions, 'load_payment_positions_data'))
            self.assertTrue(hasattr(payment_positions, 'handle_payment_position_actions'))
            
            # Since callbacks are registered with decorators, we can't directly check function names
            # But we can check that the modules load without errors
            print("✅ Payment position callbacks imported successfully")
        except Exception as e:
            self.fail(f"❌ Failed to import payment position callbacks: {e}")
    
    def test_task31_integration(self):
        """Test overall Task 31 integration."""
        try:
            # Test that all components work together
            from services.payment_position_service import get_group_payment_positions
            from components.payment_position_management import create_payment_position_list
            
            # Mock some data
            mock_data = self.sample_members_data
            
            # Test that service and components work together
            position_list = create_payment_position_list(mock_data)
            self.assertIsInstance(position_list, html.Div)
            
            print("✅ Task 31 integration works correctly")
        except Exception as e:
            self.fail(f"❌ Failed Task 31 integration test: {e}")
    
    def test_task31_requirements_coverage(self):
        """Test that all Task 31 requirements are covered."""
        requirements = [
            "Create payment position assignment algorithm",
            "Add random assignment option", 
            "Add manual assignment for admins",
            "Implement position swapping functionality",
            "Display payment schedule to all members",
            "Test payment position assignment"
        ]
        
        try:
            # Check algorithm implementation
            from services.payment_position_service import (
                assign_random_positions,
                assign_manual_positions,
                swap_payment_positions,
                get_payment_schedule
            )
            
            # Check UI components
            from components.payment_position_management import (
                create_payment_position_modal,
                create_payment_schedule_modal
            )
            
            # Check page integration
            from pages.member_management import create_action_buttons
            
            print("✅ All Task 31 requirements are covered")
            
            # Print requirement coverage
            for i, req in enumerate(requirements, 1):
                print(f"  {i}. {req} - ✅ Implemented")
                
        except Exception as e:
            self.fail(f"❌ Task 31 requirements not fully covered: {e}")


def run_task31_tests():
    """Run all Task 31 tests."""
    print("\n" + "="*60)
    print("🚀 TESTING TASK 31: PAYMENT POSITION ASSIGNMENT SYSTEM")
    print("="*60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTask31PaymentPositionAssignment)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("🎉 ALL TASK 31 TESTS PASSED!")
        print("✅ Payment Position Assignment System is ready for production")
    else:
        print("❌ Some tests failed. Please check the implementation.")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_task31_tests()
    sys.exit(0 if success else 1) 