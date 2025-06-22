"""
Group Service Module for Ajo Platform

This module provides business logic for group operations including:
- Group creation with validation
- Setting group creator as administrator
- Generating unique group invitation codes
- Group parameter validation

Task 27: Implement Group Creation Logic
"""

import secrets
import string
import psycopg2
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, Optional
import sys
import os

# Add the parent directory to sys.path to import functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions.database import get_ajo_db_connection
from functions.group_membership_service import add_member_to_group


def generate_invitation_code(length: int = 8) -> str:
    """Generate a unique invitation code for the group.
    
    Args:
        length (int): Length of the invitation code (default: 8)
        
    Returns:
        str: Unique invitation code
    """
    # Use uppercase letters and digits for readability
    characters = string.ascii_uppercase + string.digits
    # Exclude similar looking characters to avoid confusion
    characters = characters.replace('0', '').replace('O', '').replace('1', '').replace('I', '')
    
    return ''.join(secrets.choice(characters) for _ in range(length))


def validate_group_parameters(group_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate group creation parameters according to Ajo business rules.
    
    Args:
        group_data (dict): Group data to validate
        
    Returns:
        dict: Validation result with 'valid' boolean and 'errors' list
    """
    errors = []
    
    # Validate group name
    name = group_data.get('name', '').strip()
    if not name:
        errors.append("Group name is required")
    elif len(name) < 3:
        errors.append("Group name must be at least 3 characters long")
    elif len(name) > 100:
        errors.append("Group name must be less than 100 characters")
    
    # Validate contribution amount (must be one of predefined amounts)
    amount = group_data.get('contribution_amount')
    if not amount:
        errors.append("Contribution amount is required")
    else:
        try:
            amount_decimal = Decimal(str(amount))
            valid_amounts = [Decimal('50'), Decimal('100'), Decimal('500'), Decimal('800')]
            if amount_decimal not in valid_amounts:
                errors.append("Contribution amount must be £50, £100, £500, or £800")
        except (ValueError, TypeError):
            errors.append("Invalid contribution amount format")
    
    # Validate frequency
    frequency = group_data.get('frequency')
    if not frequency:
        errors.append("Contribution frequency is required")
    elif frequency not in ['weekly', 'monthly']:
        errors.append("Frequency must be 'weekly' or 'monthly'")
    
    # Validate duration (3-24 months)
    duration = group_data.get('duration_months')
    if not duration:
        errors.append("Duration is required")
    elif not isinstance(duration, int) or duration < 3 or duration > 24:
        errors.append("Duration must be between 3 and 24 months")
    
    # Validate max members (5-10 for Ajo groups)
    max_members = group_data.get('max_members')
    if not max_members:
        errors.append("Maximum members is required")
    elif not isinstance(max_members, int) or max_members < 5 or max_members > 10:
        errors.append("Maximum members must be between 5 and 10")
    
    # Validate start date
    start_date = group_data.get('start_date')
    if not start_date:
        errors.append("Start date is required")
    else:
        try:
            if isinstance(start_date, str):
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            else:
                start_date_obj = start_date
            
            today = date.today()
            if start_date_obj <= today:
                errors.append("Start date must be in the future")
            elif start_date_obj > today.replace(year=today.year + 1):
                errors.append("Start date cannot be more than 1 year in the future")
        except (ValueError, TypeError):
            errors.append("Invalid start date format")
    
    # Validate creator email
    creator_email = group_data.get('created_by_email')
    if not creator_email:
        errors.append("Creator email is required")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def get_user_id_by_email(email: str) -> Optional[int]:
    """Get user ID by email address.
    
    Args:
        email (str): User email address
        
    Returns:
        int or None: User ID if found, None otherwise
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return None
            
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return result[0] if result else None
        
    except psycopg2.Error as e:
        print(f"Database error getting user ID: {e}")
        return None


def create_group(group_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new Ajo group with validation and business logic.
    
    Args:
        group_data (dict): Group creation data containing:
            - name: Group name
            - description: Optional group description
            - contribution_amount: Decimal amount for contributions
            - frequency: 'weekly' or 'monthly'
            - start_date: Group start date
            - duration_months: Duration in months (3-24)
            - max_members: Maximum number of members (5-10)
            - created_by_email: Email of the group creator
            
    Returns:
        dict: Result with 'success' boolean, 'group_id' if successful, or 'error' message
    """
    try:
        # Validate group parameters
        validation_result = validate_group_parameters(group_data)
        if not validation_result['valid']:
            return {
                'success': False,
                'error': '; '.join(validation_result['errors'])
            }
        
        # Get user ID from email
        creator_email = group_data['created_by_email']
        creator_id = get_user_id_by_email(creator_email)
        if not creator_id:
            return {
                'success': False,
                'error': f"User with email {creator_email} not found"
            }
        
        # Generate unique invitation code
        invitation_code = generate_invitation_code()
        
        # Ensure invitation code is unique
        conn = get_ajo_db_connection()
        if not conn:
            return {
                'success': False,
                'error': 'Database connection failed'
            }
        
        cursor = conn.cursor()
        
        # Check for invitation code uniqueness and regenerate if needed
        max_attempts = 10
        attempts = 0
        while attempts < max_attempts:
            cursor.execute("SELECT id FROM ajo_groups WHERE invitation_code = %s", (invitation_code,))
            if not cursor.fetchone():
                break
            invitation_code = generate_invitation_code()
            attempts += 1
        
        if attempts >= max_attempts:
            cursor.close()
            conn.close()
            return {
                'success': False,
                'error': 'Failed to generate unique invitation code'
            }
        
        # Prepare group data for insertion
        insert_data = {
            'name': group_data['name'].strip(),
            'description': group_data.get('description', '').strip() or None,
            'contribution_amount': Decimal(str(group_data['contribution_amount'])),
            'frequency': group_data['frequency'],
            'start_date': group_data['start_date'],
            'duration_months': group_data['duration_months'],
            'max_members': group_data['max_members'],
            'status': 'active',  # Initial status for new groups
            'created_by': creator_id,
            'invitation_code': invitation_code
        }
        
        # Insert group into database
        insert_query = """
            INSERT INTO ajo_groups (
                name, description, contribution_amount, frequency, start_date,
                duration_months, max_members, status, created_by, invitation_code,
                created_at
            ) VALUES (
                %(name)s, %(description)s, %(contribution_amount)s, %(frequency)s, %(start_date)s,
                %(duration_months)s, %(max_members)s, %(status)s, %(created_by)s, %(invitation_code)s,
                NOW()
            ) RETURNING id;
        """
        
        cursor.execute(insert_query, insert_data)
        group_id = cursor.fetchone()[0]
        conn.commit()
        
        # Set group creator as administrator
        membership_result = add_member_to_group(group_id, creator_id, role='admin', payment_position=1)
        
        if not membership_result['success']:
            # Rollback group creation if membership creation fails
            cursor.execute("DELETE FROM ajo_groups WHERE id = %s", (group_id,))
            conn.commit()
            cursor.close()
            conn.close()
            return {
                'success': False,
                'error': f"Failed to set creator as admin: {membership_result.get('error', 'Unknown error')}"
            }
        
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'group_id': group_id,
            'invitation_code': invitation_code,
            'message': f"Group '{group_data['name']}' created successfully"
        }
        
    except psycopg2.Error as e:
        print(f"Database error creating group: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return {
            'success': False,
            'error': f"Database error: {str(e)}"
        }
    except Exception as e:
        print(f"Unexpected error creating group: {e}")
        if 'conn' in locals() and 'cursor' in locals():
            cursor.close()
            conn.close()
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}"
        }


def get_group_by_id(group_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a group by its ID.
    
    Args:
        group_id (int): Group ID
        
    Returns:
        dict or None: Group data if found, None otherwise
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return None
            
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, description, contribution_amount, frequency, start_date,
                   duration_months, max_members, status, created_by, invitation_code,
                   created_at, end_date
            FROM ajo_groups 
            WHERE id = %s
        """, (group_id,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'name': result[1],
                'description': result[2],
                'contribution_amount': result[3],
                'frequency': result[4],
                'start_date': result[5],
                'duration_months': result[6],
                'max_members': result[7],
                'status': result[8],
                'created_by': result[9],
                'invitation_code': result[10],
                'created_at': result[11],
                'end_date': result[12]
            }
        return None
        
    except psycopg2.Error as e:
        print(f"Database error retrieving group: {e}")
        return None


def get_groups_by_creator(creator_id: int) -> list:
    """Get all groups created by a specific user.
    
    Args:
        creator_id (int): Creator user ID
        
    Returns:
        list: List of group dictionaries
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return []
            
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, description, contribution_amount, frequency, start_date,
                   duration_months, max_members, status, created_by, invitation_code,
                   created_at, end_date
            FROM ajo_groups 
            WHERE created_by = %s
            ORDER BY created_at DESC
        """, (creator_id,))
        
        groups = []
        for row in cursor.fetchall():
            groups.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'contribution_amount': row[3],
                'frequency': row[4],
                'start_date': row[5],
                'duration_months': row[6],
                'max_members': row[7],
                'status': row[8],
                'created_by': row[9],
                'invitation_code': row[10],
                'created_at': row[11],
                'end_date': row[12]
            })
        
        cursor.close()
        conn.close()
        return groups
        
    except psycopg2.Error as e:
        print(f"Database error retrieving groups by creator: {e}")
        return [] 