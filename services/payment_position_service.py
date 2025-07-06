"""
Payment Position Service Module for Ajo Platform

This module provides business logic for managing payment positions in Ajo groups,
including position assignment algorithms, swapping, and validation.

Task 31: Implement Payment Position Assignment
"""

import psycopg2
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import sys
import os

# Add the parent directory to sys.path to import functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions.database import get_ajo_db_connection


def get_group_payment_positions(group_id: int) -> List[Dict]:
    """Get all members with their payment positions for a group.
    
    Args:
        group_id (int): ID of the group
        
    Returns:
        list: List of member dictionaries with payment positions
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return []
            
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT gm.id, gm.user_id, gm.payment_position, gm.role, gm.status,
                   u.full_name, u.email, gm.join_date
            FROM group_members gm
            JOIN users u ON gm.user_id = u.id
            WHERE gm.group_id = %s AND gm.status = 'active'
            ORDER BY gm.payment_position NULLS LAST, gm.join_date ASC
        """, (group_id,))
        
        members = []
        for row in cursor.fetchall():
            members.append({
                'membership_id': row[0],
                'user_id': row[1],
                'payment_position': row[2],
                'role': row[3],
                'status': row[4],
                'full_name': row[5],
                'email': row[6],
                'join_date': row[7]
            })
        
        cursor.close()
        conn.close()
        
        return members
        
    except psycopg2.Error as e:
        print(f"Database error getting payment positions: {e}")
        return []


def assign_random_positions(group_id: int) -> Dict[str, any]:
    """Randomly assign payment positions to all active group members.
    
    Args:
        group_id (int): ID of the group
        
    Returns:
        dict: Result with 'success' boolean and 'message' or 'error'
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return {'success': False, 'error': 'Database connection failed'}
            
        cursor = conn.cursor()
        
        # Get all active members
        cursor.execute("""
            SELECT id, user_id, full_name
            FROM group_members gm
            JOIN users u ON gm.user_id = u.id
            WHERE gm.group_id = %s AND gm.status = 'active'
        """, (group_id,))
        
        members = cursor.fetchall()
        if not members:
            cursor.close()
            conn.close()
            return {'success': False, 'error': 'No active members found'}
        
        # Create random position assignments
        positions = list(range(1, len(members) + 1))
        random.shuffle(positions)
        
        # Update positions in database
        for i, member in enumerate(members):
            cursor.execute("""
                UPDATE group_members 
                SET payment_position = %s 
                WHERE id = %s
            """, (positions[i], member[0]))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'message': f'Successfully assigned random positions to {len(members)} members',
            'assigned_count': len(members)
        }
        
    except psycopg2.Error as e:
        print(f"Database error in random assignment: {e}")
        return {'success': False, 'error': f'Database error: {str(e)}'}


def assign_manual_positions(group_id: int, position_assignments: List[Dict]) -> Dict[str, any]:
    """Manually assign specific positions to members.
    
    Args:
        group_id (int): ID of the group
        position_assignments (list): List of {'user_id': int, 'position': int}
        
    Returns:
        dict: Result with 'success' boolean and 'message' or 'error'
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return {'success': False, 'error': 'Database connection failed'}
            
        cursor = conn.cursor()
        
        # Validate positions are unique and sequential
        positions = [assignment['position'] for assignment in position_assignments]
        if len(set(positions)) != len(positions):
            return {'success': False, 'error': 'Positions must be unique'}
        
        if not all(isinstance(pos, int) and pos > 0 for pos in positions):
            return {'success': False, 'error': 'Positions must be positive integers'}
        
        # Validate all users belong to the group
        user_ids = [assignment['user_id'] for assignment in position_assignments]
        cursor.execute("""
            SELECT COUNT(*) FROM group_members 
            WHERE group_id = %s AND user_id = ANY(%s) AND status = 'active'
        """, (group_id, user_ids))
        
        valid_count = cursor.fetchone()[0]
        if valid_count != len(user_ids):
            return {'success': False, 'error': 'Some users are not active members of this group'}
        
        # Update positions
        for assignment in position_assignments:
            cursor.execute("""
                UPDATE group_members 
                SET payment_position = %s 
                WHERE group_id = %s AND user_id = %s AND status = 'active'
            """, (assignment['position'], group_id, assignment['user_id']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'message': f'Successfully assigned positions to {len(position_assignments)} members',
            'assigned_count': len(position_assignments)
        }
        
    except psycopg2.Error as e:
        print(f"Database error in manual assignment: {e}")
        return {'success': False, 'error': f'Database error: {str(e)}'}


def swap_payment_positions(group_id: int, user_id_1: int, user_id_2: int) -> Dict[str, any]:
    """Swap payment positions between two members.
    
    Args:
        group_id (int): ID of the group
        user_id_1 (int): First user ID
        user_id_2 (int): Second user ID
        
    Returns:
        dict: Result with 'success' boolean and 'message' or 'error'
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return {'success': False, 'error': 'Database connection failed'}
            
        cursor = conn.cursor()
        
        # Get current positions
        cursor.execute("""
            SELECT user_id, payment_position, full_name
            FROM group_members gm
            JOIN users u ON gm.user_id = u.id
            WHERE gm.group_id = %s AND gm.user_id IN (%s, %s) AND gm.status = 'active'
        """, (group_id, user_id_1, user_id_2))
        
        members = cursor.fetchall()
        if len(members) != 2:
            return {'success': False, 'error': 'Both users must be active members of the group'}
        
        # Extract positions
        member_1 = next((m for m in members if m[0] == user_id_1), None)
        member_2 = next((m for m in members if m[0] == user_id_2), None)
        
        if not member_1 or not member_2:
            return {'success': False, 'error': 'Could not find both members'}
        
        position_1 = member_1[1]
        position_2 = member_2[1]
        
        if position_1 is None or position_2 is None:
            return {'success': False, 'error': 'Both members must have assigned positions'}
        
        # Swap positions
        cursor.execute("""
            UPDATE group_members 
            SET payment_position = %s 
            WHERE group_id = %s AND user_id = %s
        """, (position_2, group_id, user_id_1))
        
        cursor.execute("""
            UPDATE group_members 
            SET payment_position = %s 
            WHERE group_id = %s AND user_id = %s
        """, (position_1, group_id, user_id_2))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'message': f'Successfully swapped positions between {member_1[2]} and {member_2[2]}',
            'swapped_members': [member_1[2], member_2[2]]
        }
        
    except psycopg2.Error as e:
        print(f"Database error in position swap: {e}")
        return {'success': False, 'error': f'Database error: {str(e)}'}


def get_payment_schedule(group_id: int) -> Dict[str, any]:
    """Get the payment schedule for a group showing the order of payouts.
    
    Args:
        group_id (int): ID of the group
        
    Returns:
        dict: Payment schedule with member order and next recipient
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return {'success': False, 'error': 'Database connection failed'}
            
        cursor = conn.cursor()
        
        # Get group details
        cursor.execute("""
            SELECT name, contribution_amount, frequency, start_date, status
            FROM ajo_groups
            WHERE id = %s
        """, (group_id,))
        
        group_result = cursor.fetchone()
        if not group_result:
            return {'success': False, 'error': 'Group not found'}
        
        # Get ordered members with positions
        cursor.execute("""
            SELECT gm.user_id, gm.payment_position, u.full_name, gm.role
            FROM group_members gm
            JOIN users u ON gm.user_id = u.id
            WHERE gm.group_id = %s AND gm.status = 'active'
            AND gm.payment_position IS NOT NULL
            ORDER BY gm.payment_position ASC
        """, (group_id,))
        
        members = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Format schedule
        schedule = []
        for member in members:
            schedule.append({
                'user_id': member[0],
                'position': member[1],
                'full_name': member[2],
                'role': member[3],
                'is_next': member[1] == 1  # First position is next to receive
            })
        
        return {
            'success': True,
            'group_name': group_result[0],
            'contribution_amount': group_result[1],
            'frequency': group_result[2],
            'start_date': group_result[3],
            'group_status': group_result[4],
            'schedule': schedule,
            'total_members': len(schedule),
            'next_recipient': schedule[0] if schedule else None
        }
        
    except psycopg2.Error as e:
        print(f"Database error getting payment schedule: {e}")
        return {'success': False, 'error': f'Database error: {str(e)}'}


def validate_payment_positions(group_id: int) -> Dict[str, any]:
    """Validate that all active members have unique, sequential payment positions.
    
    Args:
        group_id (int): ID of the group
        
    Returns:
        dict: Validation result with issues found
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return {'success': False, 'error': 'Database connection failed'}
            
        cursor = conn.cursor()
        
        # Get all active members and their positions
        cursor.execute("""
            SELECT gm.user_id, gm.payment_position, u.full_name
            FROM group_members gm
            JOIN users u ON gm.user_id = u.id
            WHERE gm.group_id = %s AND gm.status = 'active'
            ORDER BY gm.payment_position NULLS LAST
        """, (group_id,))
        
        members = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not members:
            return {'success': True, 'valid': True, 'message': 'No active members found'}
        
        issues = []
        positions = []
        members_without_positions = []
        
        for member in members:
            user_id, position, full_name = member
            if position is None:
                members_without_positions.append(full_name)
            else:
                positions.append(position)
        
        # Check for missing positions
        if members_without_positions:
            issues.append(f"Members without positions: {', '.join(members_without_positions)}")
        
        # Check for duplicate positions
        if len(positions) != len(set(positions)):
            duplicates = [pos for pos in positions if positions.count(pos) > 1]
            issues.append(f"Duplicate positions found: {', '.join(map(str, set(duplicates)))}")
        
        # Check for sequential positions (should be 1, 2, 3, ...)
        if positions:
            expected_positions = set(range(1, len(members) + 1))
            actual_positions = set(positions)
            
            if actual_positions != expected_positions:
                missing = expected_positions - actual_positions
                extra = actual_positions - expected_positions
                
                if missing:
                    issues.append(f"Missing positions: {', '.join(map(str, sorted(missing)))}")
                if extra:
                    issues.append(f"Invalid positions: {', '.join(map(str, sorted(extra)))}")
        
        return {
            'success': True,
            'valid': len(issues) == 0,
            'total_members': len(members),
            'assigned_positions': len(positions),
            'issues': issues,
            'message': 'All positions are valid' if len(issues) == 0 else f'Found {len(issues)} issue(s)'
        }
        
    except psycopg2.Error as e:
        print(f"Database error validating positions: {e}")
        return {'success': False, 'error': f'Database error: {str(e)}'}


def auto_assign_missing_positions(group_id: int) -> Dict[str, any]:
    """Automatically assign positions to members who don't have them.
    
    Args:
        group_id (int): ID of the group
        
    Returns:
        dict: Result with 'success' boolean and assignment details
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return {'success': False, 'error': 'Database connection failed'}
            
        cursor = conn.cursor()
        
        # Get members without positions
        cursor.execute("""
            SELECT gm.id, gm.user_id, u.full_name
            FROM group_members gm
            JOIN users u ON gm.user_id = u.id
            WHERE gm.group_id = %s AND gm.status = 'active' 
            AND gm.payment_position IS NULL
            ORDER BY gm.join_date ASC
        """, (group_id,))
        
        members_without_positions = cursor.fetchall()
        
        if not members_without_positions:
            return {'success': True, 'message': 'All members already have positions assigned'}
        
        # Get highest existing position
        cursor.execute("""
            SELECT COALESCE(MAX(payment_position), 0)
            FROM group_members
            WHERE group_id = %s AND status = 'active'
        """, (group_id,))
        
        max_position = cursor.fetchone()[0]
        
        # Assign sequential positions starting from max + 1
        assigned_members = []
        for i, member in enumerate(members_without_positions):
            new_position = max_position + i + 1
            cursor.execute("""
                UPDATE group_members 
                SET payment_position = %s 
                WHERE id = %s
            """, (new_position, member[0]))
            
            assigned_members.append({
                'user_id': member[1],
                'full_name': member[2],
                'position': new_position
            })
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'message': f'Assigned positions to {len(assigned_members)} members',
            'assigned_members': assigned_members,
            'assigned_count': len(assigned_members)
        }
        
    except psycopg2.Error as e:
        print(f"Database error in auto-assignment: {e}")
        return {'success': False, 'error': f'Database error: {str(e)}'} 