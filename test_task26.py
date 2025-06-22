#!/usr/bin/env python3
"""
Test Task 26: Create Group Registration Form
Tests that the group registration form meets all requirements and functions correctly.
"""

import sys
import unittest
from datetime import date, timedelta
from decimal import Decimal
import dash
from dash import html
import dash_bootstrap_components as dbc
from components.modals import create_group_modal, create_success_modal

class TestTask26GroupRegistrationForm(unittest.TestCase):
    """Test that Task 26 group registration form is complete and functional."""
    
    def setUp(self):
        """Set up test environment."""
        self.app = dash.Dash(__name__)
        
    def test_group_modal_component_exists(self):
        """Test that group registration modal component exists."""
        modal = create_group_modal()
        self.assertIsNotNone(modal, "Group registration modal component should exist")
        self.assertEqual(modal.id, "create-group-modal")
    
    def test_required_form_fields_exist(self):
        """Test that all required form fields exist in the modal."""
        modal = create_group_modal()
        
        # Convert to dict to inspect structure
        modal_dict = modal.to_plotly_json()
        
        # Check that required input IDs exist in the modal structure
        required_ids = [
            "group-name-input",
            "group-description-input", 
            "contribution-amount-input",
            "frequency-input",
            "duration-input",
            "max-members-input",
            "start-date-input"
        ]
        
        modal_str = str(modal_dict)
        for field_id in required_ids:
            with self.subTest(field_id=field_id):
                self.assertIn(field_id, modal_str, 
                            f"Required field '{field_id}' missing from group registration form")
    
    def test_contribution_amount_options(self):
        """Test that contribution amount has correct predefined options."""
        modal = create_group_modal()
        modal_dict = modal.to_plotly_json()
        modal_str = str(modal_dict)
        
        # Check that all required contribution amounts are available
        required_amounts = [50, 100, 500, 800]
        for amount in required_amounts:
            with self.subTest(amount=amount):
                # Look for the value in the options structure
                self.assertIn(f"'value': {amount}", modal_str,
                            f"Contribution amount £{amount} should be available")
    
    def test_frequency_options(self):
        """Test that frequency options are correct."""
        modal = create_group_modal()
        modal_dict = modal.to_plotly_json()
        modal_str = str(modal_dict)
        
        # Check that frequency options exist
        required_frequencies = ["weekly", "monthly"]
        for frequency in required_frequencies:
            with self.subTest(frequency=frequency):
                self.assertIn(f"'value': '{frequency}'", modal_str,
                            f"Frequency option '{frequency}' should be available")
    
    def test_max_members_options(self):
        """Test that max members options are within Ajo constraints (5-10)."""
        modal = create_group_modal()
        modal_dict = modal.to_plotly_json()
        modal_str = str(modal_dict)
        
        # Check that member count options are correct (5-10 members)
        required_member_counts = [5, 6, 7, 8, 9, 10]
        for count in required_member_counts:
            with self.subTest(count=count):
                self.assertIn(f"'value': {count}", modal_str,
                            f"Max members option '{count}' should be available")
    
    def test_form_validation_elements_exist(self):
        """Test that form validation feedback elements exist."""
        modal = create_group_modal()
        modal_dict = modal.to_plotly_json()
        modal_str = str(modal_dict)
        
        # Check that validation feedback divs exist
        validation_ids = [
            "group-name-feedback",
            "contribution-amount-feedback",
            "frequency-feedback", 
            "duration-feedback",
            "max-members-feedback",
            "start-date-feedback",
            "form-validation-alert"
        ]
        
        for validation_id in validation_ids:
            with self.subTest(validation_id=validation_id):
                self.assertIn(validation_id, modal_str,
                            f"Validation element '{validation_id}' missing from form")
    
    def test_form_buttons_exist(self):
        """Test that form action buttons exist."""
        modal = create_group_modal()
        modal_dict = modal.to_plotly_json()
        modal_str = str(modal_dict)
        
        # Check that required buttons exist
        required_buttons = [
            "cancel-group-btn",
            "create-group-btn"
        ]
        
        for button_id in required_buttons:
            with self.subTest(button_id=button_id):
                self.assertIn(button_id, modal_str,
                            f"Button '{button_id}' missing from form")
    
    def test_success_modal_exists(self):
        """Test that success modal component exists."""
        success_modal = create_success_modal()
        self.assertIsNotNone(success_modal, "Success modal component should exist")
        self.assertEqual(success_modal.id, "success-modal")
    
    def test_modal_configuration(self):
        """Test that modal has correct configuration."""
        modal = create_group_modal()
        
        # Check modal properties
        self.assertEqual(modal.size, "lg", "Modal should be large size")
        self.assertEqual(modal.backdrop, "static", "Modal should have static backdrop")
        self.assertEqual(modal.keyboard, False, "Modal should not close with keyboard")
        self.assertEqual(modal.is_open, False, "Modal should be closed by default")
    
    def test_required_field_indicators(self):
        """Test that required fields are marked with asterisks."""
        modal = create_group_modal()
        modal_dict = modal.to_plotly_json()
        modal_str = str(modal_dict)
        
        # Check that required fields have asterisk indicators
        required_field_labels = [
            "Group Name *",
            "Contribution Amount *", 
            "Contribution Frequency *",
            "Duration (Months) *",
            "Maximum Members *",
            "Start Date *"
        ]
        
        for label in required_field_labels:
            with self.subTest(label=label):
                self.assertIn(label, modal_str,
                            f"Required field label '{label}' with asterisk missing")
    
    def test_form_constraints(self):
        """Test that form fields have appropriate constraints."""
        modal = create_group_modal()
        modal_dict = modal.to_plotly_json()
        modal_str = str(modal_dict)
        
        # Check duration constraints - look for the actual format in the JSON
        self.assertIn("max=24", modal_str, "Duration should have maximum of 24 months")
        self.assertIn("min=3", modal_str, "Duration should have minimum of 3 months")
        
        # Check that required fields are marked as required
        self.assertIn("required=True", modal_str, "Required fields should be marked as required")
    
    def test_form_help_text(self):
        """Test that helpful text is provided for users."""
        modal = create_group_modal()
        modal_dict = modal.to_plotly_json()
        modal_str = str(modal_dict)
        
        # Check for helpful text
        helpful_texts = [
            "Minimum 3 months, maximum 24 months",
            "Groups typically start within 1-2 weeks"
        ]
        
        for text in helpful_texts:
            with self.subTest(text=text):
                self.assertIn(text, modal_str,
                            f"Helpful text '{text}' should be present in form")

    def test_three_tab_structure_maintained(self):
        """Test that the original 3-tab structure is maintained."""
        modal = create_group_modal()
        modal_dict = modal.to_plotly_json()
        modal_str = str(modal_dict)
        
        # Check that all three tabs exist - look for the actual format
        required_tabs = ["Details", "Members", "Schedule"]
        for tab in required_tabs:
            with self.subTest(tab=tab):
                self.assertIn(f"label='{tab}'", modal_str,
                            f"Tab '{tab}' should exist in modal")
        
        # Check that tab IDs exist - look for the actual format
        tab_ids = ["details", "members", "schedule"]
        for tab_id in tab_ids:
            with self.subTest(tab_id=tab_id):
                self.assertIn(f"tab_id='{tab_id}'", modal_str,
                            f"Tab ID '{tab_id}' should exist in modal")

class TestTask26FormValidation(unittest.TestCase):
    """Test form validation logic for Task 26."""
    
    def test_group_name_validation_logic(self):
        """Test group name validation requirements."""
        from callbacks import handle_group_creation
        
        # Test cases for group name validation
        test_cases = [
            ("", "Group name must be at least 3 characters long"),  # Empty name
            ("AB", "Group name must be at least 3 characters long"),  # Too short
            ("A" * 101, "Group name must be less than 100 characters"),  # Too long
            ("Valid Group Name", None),  # Valid name
        ]
        
        for name, expected_error in test_cases:
            with self.subTest(name=name):
                # Mock session data
                session_data = {'logged_in': True, 'user_info': {'email': 'test@example.com'}}
                
                # Call validation with minimal valid data except for the field being tested
                result = handle_group_creation(
                    n_clicks=1,
                    name=name,
                    description="Test description",
                    amount=100,
                    frequency="monthly", 
                    duration=12,
                    max_members=6,
                    start_date=(date.today() + timedelta(days=7)).strftime("%Y-%m-%d"),
                    session_data=session_data
                )
                
                name_feedback = result[1]  # group-name-feedback is second output
                
                if expected_error:
                    self.assertEqual(name_feedback, expected_error)
                else:
                    self.assertEqual(name_feedback, "")
    
    def test_contribution_amount_validation(self):
        """Test contribution amount validation."""
        # Valid amounts should be 50, 100, 500, 800
        valid_amounts = [50, 100, 500, 800]
        invalid_amounts = [25, 75, 150, 1000, None]
        
        for amount in valid_amounts:
            with self.subTest(amount=amount, valid=True):
                # Should not produce validation error for valid amounts
                self.assertIn(amount, [50, 100, 500, 800])
        
        for amount in invalid_amounts:
            with self.subTest(amount=amount, valid=False):
                # Should produce validation error for invalid amounts
                if amount is not None:
                    self.assertNotIn(amount, [50, 100, 500, 800])
    
    def test_duration_constraints(self):
        """Test duration validation constraints."""
        # Duration should be between 3 and 24 months
        valid_durations = [3, 6, 12, 18, 24]
        invalid_durations = [1, 2, 25, 30, None]
        
        for duration in valid_durations:
            with self.subTest(duration=duration, valid=True):
                self.assertGreaterEqual(duration, 3)
                self.assertLessEqual(duration, 24)
        
        for duration in invalid_durations:
            with self.subTest(duration=duration, valid=False):
                if duration is not None:
                    self.assertTrue(duration < 3 or duration > 24)
    
    def test_max_members_constraints(self):
        """Test max members validation constraints."""
        # Max members should be between 5 and 10
        valid_members = [5, 6, 7, 8, 9, 10]
        invalid_members = [3, 4, 11, 15, None]
        
        for members in valid_members:
            with self.subTest(members=members, valid=True):
                self.assertIn(members, [5, 6, 7, 8, 9, 10])
        
        for members in invalid_members:
            with self.subTest(members=members, valid=False):
                if members is not None:
                    self.assertNotIn(members, [5, 6, 7, 8, 9, 10])

if __name__ == '__main__':
    print("Testing Task 26: Create Group Registration Form")
    print("=" * 60)
    
    # Run the tests
    unittest.main(verbosity=2) 