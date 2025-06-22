"""
Group Membership Service Module for Ajo Platform

This module provides database operations for group membership management,
including adding/removing members, role management, and payment position assignment.
"""

import psycopg2
from datetime import datetime, date
from .database import get_ajo_db_connection


def add_member_to_group(group_id, user_id, role='member', payment_position=None):
    """Add a user to a group with specified role and payment position.
    
    Args:
        group_id (int): ID of the group
        user_id (int): ID of the user to add
        role (str): Role of the member ('admin' or 'member')
        payment_position (int, optional): Payment position (auto-assigned if None)
        
    Returns:
        dict: Result with 'success' boolean and 'member_id' or 'error'
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return {'success': False, 'error': 'Database connection failed'}
            
        cursor = conn.cursor()
        
        # Check if user is already a member of this group
        cursor.execute("""
            SELECT id FROM group_members 
            WHERE group_id = %s AND user_id = %s
        """, (group_id, user_id))
        
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {'success': False, 'error': 'User is already a member of this group'}
        
        # Check if group exists and get max_members
        cursor.execute("""
            SELECT max_members, 
                   (SELECT COUNT(*) FROM group_members WHERE group_id = %s AND status = 'active') as current_members
            FROM ajo_groups WHERE id = %s
        """, (group_id, group_id))
        
        group_info = cursor.fetchone()
        if not group_info:
            cursor.close()
            conn.close()
            return {'success': False, 'error': 'Group not found'}
        
        max_members, current_members = group_info
        if current_members >= max_members:
            cursor.close()
            conn.close()
            return {'success': False, 'error': f'Group is full (max {max_members} members)'}
        
        # Auto-assign payment position if not provided
        if payment_position is None:
            cursor.execute("""
                SELECT COALESCE(MAX(payment_position), 0) + 1
                FROM group_members 
                WHERE group_id = %s
            """, (group_id,))
            payment_position = cursor.fetchone()[0]
        
        # Verify payment position is not already taken
        cursor.execute("""
            SELECT id FROM group_members 
            WHERE group_id = %s AND payment_position = %s
        """, (group_id, payment_position))
        
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {'success': False, 'error': f'Payment position {payment_position} is already taken'}
        
        # Insert new member
        cursor.execute("""
            INSERT INTO group_members (group_id, user_id, role, payment_position)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (group_id, user_id, role, payment_position))
        
        member_id = cursor.fetchone()[0]
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {
            'success': True, 
            'member_id': member_id,
            'payment_position': payment_position
        }
        
    except psycopg2.Error as e:
        return {'success': False, 'error': f'Database error: {str(e)}'}


def remove_member_from_group(group_id, user_id):
    """Remove a user from a group.
    
    Args:
        group_id (int): ID of the group
        user_id (int): ID of the user to remove
        
    Returns:
        dict: Result with 'success' boolean and 'error' if applicable
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return {'success': False, 'error': 'Database connection failed'}
            
        cursor = conn.cursor()
        
        # Check if user is a member of this group
        cursor.execute("""
            SELECT id, role FROM group_members 
            WHERE group_id = %s AND user_id = %s AND status = 'active'
        """, (group_id, user_id))
        
        member_info = cursor.fetchone()
        if not member_info:
            cursor.close()
            conn.close()
            return {'success': False, 'error': 'User is not an active member of this group'}
        
        member_id, role = member_info
        
        # Check if this is the last admin (prevent removing last admin)
        if role == 'admin':
            cursor.execute("""
                SELECT COUNT(*) FROM group_members 
                WHERE group_id = %s AND role = 'admin' AND status = 'active'
            """, (group_id,))
            
            admin_count = cursor.fetchone()[0]
            if admin_count <= 1:
                cursor.close()
                conn.close()
                return {'success': False, 'error': 'Cannot remove the last admin from the group'}
        
        # Mark member as removed (soft delete)
        cursor.execute("""
            UPDATE group_members 
            SET status = 'removed'
            WHERE id = %s
        """, (member_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {'success': True}
        
    except psycopg2.Error as e:
        return {'success': False, 'error': f'Database error: {str(e)}'}


def update_member_role(group_id, user_id, new_role):
    """Update a member's role in a group.
    
    Args:
        group_id (int): ID of the group
        user_id (int): ID of the user
        new_role (str): New role ('admin' or 'member')
        
    Returns:
        dict: Result with 'success' boolean and 'error' if applicable
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return {'success': False, 'error': 'Database connection failed'}
            
        cursor = conn.cursor()
        
        # Check if user is a member of this group
        cursor.execute("""
            SELECT id, role FROM group_members 
            WHERE group_id = %s AND user_id = %s AND status = 'active'
        """, (group_id, user_id))
        
        member_info = cursor.fetchone()
        if not member_info:
            cursor.close()
            conn.close()
            return {'success': False, 'error': 'User is not an active member of this group'}
        
        member_id, current_role = member_info
        
        # Check if demoting last admin
        if current_role == 'admin' and new_role == 'member':
            cursor.execute("""
                SELECT COUNT(*) FROM group_members 
                WHERE group_id = %s AND role = 'admin' AND status = 'active'
            """, (group_id,))
            
            admin_count = cursor.fetchone()[0]
            if admin_count <= 1:
                cursor.close()
                conn.close()
                return {'success': False, 'error': 'Cannot demote the last admin of the group'}
        
        # Update role
        cursor.execute("""
            UPDATE group_members 
            SET role = %s
            WHERE id = %s
        """, (new_role, member_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {'success': True}
        
    except psycopg2.Error as e:
        return {'success': False, 'error': f'Database error: {str(e)}'}


def get_group_members(group_id, include_inactive=False):
    """Get all members of a group.
    
    Args:
        group_id (int): ID of the group
        include_inactive (bool): Whether to include inactive/removed members
        
    Returns:
        list: List of member dictionaries or None if error
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return None
            
        cursor = conn.cursor()
        
        status_filter = "" if include_inactive else "AND gm.status = 'active'"
        
        cursor.execute(f"""
            SELECT gm.id, gm.user_id, u.full_name, u.email, gm.role, 
                   gm.payment_position, gm.join_date, gm.status, gm.created_at
            FROM group_members gm
            JOIN users u ON gm.user_id = u.id
            WHERE gm.group_id = %s {status_filter}
            ORDER BY gm.payment_position, gm.join_date
        """, (group_id,))
        
        members = []
        for row in cursor.fetchall():
            members.append({
                'id': row[0],
                'user_id': row[1],
                'full_name': row[2],
                'email': row[3],
                'role': row[4],
                'payment_position': row[5],
                'join_date': row[6],
                'status': row[7],
                'created_at': row[8]
            })
        
        cursor.close()
        conn.close()
        
        return members
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None


def get_user_groups(user_id, include_inactive=False):
    """Get all groups a user is a member of.
    
    Args:
        user_id (int): ID of the user
        include_inactive (bool): Whether to include inactive memberships
        
    Returns:
        list: List of group membership dictionaries or None if error
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return None
            
        cursor = conn.cursor()
        
        status_filter = "" if include_inactive else "AND gm.status = 'active'"
        
        cursor.execute(f"""
            SELECT gm.id, gm.group_id, ag.name, ag.description, ag.contribution_amount,
                   ag.frequency, gm.role, gm.payment_position, gm.join_date, gm.status,
                   ag.start_date, ag.end_date, ag.status as group_status
            FROM group_members gm
            JOIN ajo_groups ag ON gm.group_id = ag.id
            WHERE gm.user_id = %s {status_filter}
            ORDER BY gm.join_date DESC
        """, (user_id,))
        
        groups = []
        for row in cursor.fetchall():
            groups.append({
                'membership_id': row[0],
                'group_id': row[1],
                'group_name': row[2],
                'group_description': row[3],
                'contribution_amount': row[4],
                'frequency': row[5],
                'role': row[6],
                'payment_position': row[7],
                'join_date': row[8],
                'membership_status': row[9],
                'start_date': row[10],
                'end_date': row[11],
                'group_status': row[12]
            })
        
        cursor.close()
        conn.close()
        
        return groups
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None


def update_payment_position(group_id, user_id, new_position):
    """Update a member's payment position in a group.
    
    Args:
        group_id (int): ID of the group
        user_id (int): ID of the user
        new_position (int): New payment position
        
    Returns:
        dict: Result with 'success' boolean and 'error' if applicable
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return {'success': False, 'error': 'Database connection failed'}
            
        cursor = conn.cursor()
        
        # Check if user is a member of this group
        cursor.execute("""
            SELECT id, payment_position FROM group_members 
            WHERE group_id = %s AND user_id = %s AND status = 'active'
        """, (group_id, user_id))
        
        member_info = cursor.fetchone()
        if not member_info:
            cursor.close()
            conn.close()
            return {'success': False, 'error': 'User is not an active member of this group'}
        
        member_id, current_position = member_info
        
        # Check if new position is already taken by another member
        cursor.execute("""
            SELECT user_id FROM group_members 
            WHERE group_id = %s AND payment_position = %s AND user_id != %s
        """, (group_id, new_position, user_id))
        
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {'success': False, 'error': f'Payment position {new_position} is already taken'}
        
        # Update payment position
        cursor.execute("""
            UPDATE group_members 
            SET payment_position = %s
            WHERE id = %s
        """, (new_position, member_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {'success': True}
        
    except psycopg2.Error as e:
        return {'success': False, 'error': f'Database error: {str(e)}'}


def get_group_admin_count(group_id):
    """Get the number of active admins in a group.
    
    Args:
        group_id (int): ID of the group
        
    Returns:
        int: Number of active admins, or -1 if error
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return -1
            
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) FROM group_members 
            WHERE group_id = %s AND role = 'admin' AND status = 'active'
        """, (group_id,))
        
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return count
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return -1


def is_user_group_member(group_id, user_id):
    """Check if a user is an active member of a group.
    
    Args:
        group_id (int): ID of the group
        user_id (int): ID of the user
        
    Returns:
        dict: Dictionary with membership info or None if not a member
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return None
            
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, role, payment_position, join_date, status
            FROM group_members 
            WHERE group_id = %s AND user_id = %s AND status = 'active'
        """, (group_id, user_id))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return {
                'membership_id': result[0],
                'role': result[1],
                'payment_position': result[2],
                'join_date': result[3],
                'status': result[4]
            }
        return None
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None 