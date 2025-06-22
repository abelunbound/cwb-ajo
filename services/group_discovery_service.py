"""
Group Discovery Service Module for Ajo Platform

This module provides business logic for group discovery operations including:
- Finding groups users can join
- Search functionality by name/description  
- Filtering by contribution amount and frequency
- Group details with member information
- Pagination for large group lists

Task 28: Build Group Discovery Interface
"""

import psycopg2
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple
import sys
import os

# Add the parent directory to sys.path to import functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions.database import get_ajo_db_connection


def get_discoverable_groups(user_id: int, page: int = 1, per_page: int = 12) -> Dict[str, Any]:
    """Get groups that a user can discover and potentially join.
    
    Args:
        user_id (int): ID of the user looking for groups
        page (int): Page number for pagination (1-based)
        per_page (int): Number of groups per page
        
    Returns:
        dict: Result with 'groups' list, 'total_count', 'page', 'per_page', 'total_pages'
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return {'success': False, 'error': 'Database connection failed'}
            
        cursor = conn.cursor()
        
        # Calculate offset for pagination
        offset = (page - 1) * per_page
        
        # Get total count first
        cursor.execute("""
            SELECT COUNT(DISTINCT ag.id)
            FROM ajo_groups ag
            WHERE ag.status = 'active'
            AND ag.id NOT IN (
                SELECT gm.group_id 
                FROM group_members gm 
                WHERE gm.user_id = %s AND gm.status = 'active'
            )
        """, (user_id,))
        
        total_count = cursor.fetchone()[0]
        total_pages = (total_count + per_page - 1) // per_page
        
        # Get groups with member information
        cursor.execute("""
            SELECT 
                ag.id, ag.name, ag.description, ag.contribution_amount, ag.frequency,
                ag.start_date, ag.duration_months, ag.max_members, ag.status,
                ag.created_at, ag.end_date,
                COUNT(gm.id) as current_members,
                u.full_name as creator_name
            FROM ajo_groups ag
            LEFT JOIN group_members gm ON ag.id = gm.group_id AND gm.status = 'active'
            LEFT JOIN users u ON ag.created_by = u.id
            WHERE ag.status = 'active'
            AND ag.id NOT IN (
                SELECT gm2.group_id 
                FROM group_members gm2 
                WHERE gm2.user_id = %s AND gm2.status = 'active'
            )
            GROUP BY ag.id, ag.name, ag.description, ag.contribution_amount, ag.frequency,
                     ag.start_date, ag.duration_months, ag.max_members, ag.status,
                     ag.created_at, ag.end_date, u.full_name
            ORDER BY ag.created_at DESC
            LIMIT %s OFFSET %s
        """, (user_id, per_page, offset))
        
        groups = []
        for row in cursor.fetchall():
            group = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'contribution_amount': row[3],
                'frequency': row[4],
                'start_date': row[5],
                'duration_months': row[6],
                'max_members': row[7],
                'status': row[8],
                'created_at': row[9],
                'end_date': row[10],
                'current_members': row[11],
                'creator_name': row[12],
                'spots_available': row[7] - row[11],  # max_members - current_members
                'is_full': row[11] >= row[7]
            }
            groups.append(group)
        
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'groups': groups,
            'total_count': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages
        }
        
    except psycopg2.Error as e:
        print(f"Database error getting discoverable groups: {e}")
        return {'success': False, 'error': f"Database error: {str(e)}"}
    except Exception as e:
        print(f"Unexpected error getting discoverable groups: {e}")
        return {'success': False, 'error': f"Unexpected error: {str(e)}"}


def search_groups(user_id: int, query: str = "", filters: Dict[str, Any] = None, 
                 page: int = 1, per_page: int = 12) -> Dict[str, Any]:
    """Search and filter groups that a user can discover.
    
    Args:
        user_id (int): ID of the user searching
        query (str): Search query for name/description
        filters (dict): Filter criteria including:
            - contribution_amount: List of amounts to filter by
            - frequency: List of frequencies to filter by
            - min_spots: Minimum available spots
        page (int): Page number for pagination
        per_page (int): Number of groups per page
        
    Returns:
        dict: Search results with groups and pagination info
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return {'success': False, 'error': 'Database connection failed'}
            
        cursor = conn.cursor()
        
        # Build WHERE conditions
        where_conditions = ["ag.status = 'active'"]
        params = [user_id]
        
        # Exclude groups user is already a member of
        where_conditions.append("""
            ag.id NOT IN (
                SELECT gm.group_id 
                FROM group_members gm 
                WHERE gm.user_id = %s AND gm.status = 'active'
            )
        """)
        
        # Add search query
        if query and query.strip():
            where_conditions.append("(ag.name ILIKE %s OR ag.description ILIKE %s)")
            search_term = f"%{query.strip()}%"
            params.extend([search_term, search_term])
        
        # Add filters
        if filters:
            # Filter by contribution amount
            if filters.get('contribution_amount'):
                amounts = filters['contribution_amount']
                if isinstance(amounts, list) and amounts:
                    placeholders = ','.join(['%s'] * len(amounts))
                    where_conditions.append(f"ag.contribution_amount IN ({placeholders})")
                    params.extend(amounts)
            
            # Filter by frequency
            if filters.get('frequency'):
                frequencies = filters['frequency']
                if isinstance(frequencies, list) and frequencies:
                    placeholders = ','.join(['%s'] * len(frequencies))
                    where_conditions.append(f"ag.frequency IN ({placeholders})")
                    params.extend(frequencies)
        
        where_clause = " AND ".join(where_conditions)
        
        # Calculate offset for pagination
        offset = (page - 1) * per_page
        
        # Get total count
        count_query = f"""
            SELECT COUNT(DISTINCT ag.id)
            FROM ajo_groups ag
            WHERE {where_clause}
        """
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]
        total_pages = (total_count + per_page - 1) // per_page
        
        # Get groups with member information
        main_query = f"""
            SELECT 
                ag.id, ag.name, ag.description, ag.contribution_amount, ag.frequency,
                ag.start_date, ag.duration_months, ag.max_members, ag.status,
                ag.created_at, ag.end_date,
                COUNT(gm.id) as current_members,
                u.full_name as creator_name
            FROM ajo_groups ag
            LEFT JOIN group_members gm ON ag.id = gm.group_id AND gm.status = 'active'
            LEFT JOIN users u ON ag.created_by = u.id
            WHERE {where_clause}
            GROUP BY ag.id, ag.name, ag.description, ag.contribution_amount, ag.frequency,
                     ag.start_date, ag.duration_months, ag.max_members, ag.status,
                     ag.created_at, ag.end_date, u.full_name
        """
        
        # Add post-GROUP BY filters
        having_conditions = []
        if filters and filters.get('min_spots'):
            min_spots = int(filters['min_spots'])
            having_conditions.append(f"(ag.max_members - COUNT(gm.id)) >= {min_spots}")
        
        if having_conditions:
            main_query += " HAVING " + " AND ".join(having_conditions)
        
        main_query += " ORDER BY ag.created_at DESC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])
        
        cursor.execute(main_query, params)
        
        groups = []
        for row in cursor.fetchall():
            group = {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'contribution_amount': row[3],
                'frequency': row[4],
                'start_date': row[5],
                'duration_months': row[6],
                'max_members': row[7],
                'status': row[8],
                'created_at': row[9],
                'end_date': row[10],
                'current_members': row[11],
                'creator_name': row[12],
                'spots_available': row[7] - row[11],
                'is_full': row[11] >= row[7]
            }
            groups.append(group)
        
        cursor.close()
        conn.close()
        
        return {
            'success': True,
            'groups': groups,
            'total_count': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'query': query,
            'filters': filters or {}
        }
        
    except psycopg2.Error as e:
        print(f"Database error searching groups: {e}")
        return {'success': False, 'error': f"Database error: {str(e)}"}
    except Exception as e:
        print(f"Unexpected error searching groups: {e}")
        return {'success': False, 'error': f"Unexpected error: {str(e)}"}


def get_group_details_for_discovery(group_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    """Get detailed information about a group for discovery purposes.
    
    Args:
        group_id (int): ID of the group
        user_id (int): ID of the user viewing the group
        
    Returns:
        dict or None: Detailed group information or None if not found/accessible
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return None
            
        cursor = conn.cursor()
        
        # Check if user is already a member
        cursor.execute("""
            SELECT id FROM group_members 
            WHERE group_id = %s AND user_id = %s AND status = 'active'
        """, (group_id, user_id))
        
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return None  # User is already a member
        
        # Get group details with member information
        cursor.execute("""
            SELECT 
                ag.id, ag.name, ag.description, ag.contribution_amount, ag.frequency,
                ag.start_date, ag.duration_months, ag.max_members, ag.status,
                ag.created_at, ag.end_date, ag.invitation_code,
                COUNT(gm.id) as current_members,
                u.full_name as creator_name, u.email as creator_email
            FROM ajo_groups ag
            LEFT JOIN group_members gm ON ag.id = gm.group_id AND gm.status = 'active'
            LEFT JOIN users u ON ag.created_by = u.id
            WHERE ag.id = %s AND ag.status = 'active'
            GROUP BY ag.id, ag.name, ag.description, ag.contribution_amount, ag.frequency,
                     ag.start_date, ag.duration_months, ag.max_members, ag.status,
                     ag.created_at, ag.end_date, ag.invitation_code, u.full_name, u.email
        """, (group_id,))
        
        result = cursor.fetchone()
        if not result:
            cursor.close()
            conn.close()
            return None
        
        # Get member details (anonymized for privacy)
        cursor.execute("""
            SELECT gm.role, gm.payment_position, u.full_name
            FROM group_members gm
            JOIN users u ON gm.user_id = u.id
            WHERE gm.group_id = %s AND gm.status = 'active'
            ORDER BY gm.payment_position
        """, (group_id,))
        
        members = []
        for member_row in cursor.fetchall():
            members.append({
                'role': member_row[0],
                'payment_position': member_row[1],
                'name': member_row[2]  # In production, you might want to anonymize this
            })
        
        cursor.close()
        conn.close()
        
        group_details = {
            'id': result[0],
            'name': result[1],
            'description': result[2],
            'contribution_amount': result[3],
            'frequency': result[4],
            'start_date': result[5],
            'duration_months': result[6],
            'max_members': result[7],
            'status': result[8],
            'created_at': result[9],
            'end_date': result[10],
            'invitation_code': result[11],  # Might be hidden in UI
            'current_members': result[12],
            'creator_name': result[13],
            'creator_email': result[14],  # Might be hidden in UI
            'spots_available': result[7] - result[12],
            'is_full': result[12] >= result[7],
            'members': members
        }
        
        return group_details
        
    except psycopg2.Error as e:
        print(f"Database error getting group details: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error getting group details: {e}")
        return None


def get_filter_options() -> Dict[str, List]:
    """Get available filter options for group discovery.
    
    Returns:
        dict: Available filter options for contribution amounts and frequencies
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return {
                'contribution_amounts': [50, 100, 500, 800],
                'frequencies': ['weekly', 'monthly']
            }
            
        cursor = conn.cursor()
        
        # Get unique contribution amounts from active groups
        cursor.execute("""
            SELECT DISTINCT contribution_amount 
            FROM ajo_groups 
            WHERE status = 'active' 
            ORDER BY contribution_amount
        """)
        amounts = [row[0] for row in cursor.fetchall()]
        
        # Get unique frequencies from active groups
        cursor.execute("""
            SELECT DISTINCT frequency 
            FROM ajo_groups 
            WHERE status = 'active' 
            ORDER BY frequency
        """)
        frequencies = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return {
            'contribution_amounts': amounts,
            'frequencies': frequencies
        }
        
    except psycopg2.Error as e:
        print(f"Database error getting filter options: {e}")
        # Return default options if database error
        return {
            'contribution_amounts': [50, 100, 500, 800],
            'frequencies': ['weekly', 'monthly']
        }


def can_user_join_group(group_id: int, user_id: int) -> Dict[str, Any]:
    """Check if a user can join a specific group.
    
    Args:
        group_id (int): ID of the group
        user_id (int): ID of the user
        
    Returns:
        dict: Result with 'can_join' boolean and 'reason' if cannot join
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return {'can_join': False, 'reason': 'Database connection failed'}
            
        cursor = conn.cursor()
        
        # Check if group exists and is active
        cursor.execute("""
            SELECT id, max_members, status 
            FROM ajo_groups 
            WHERE id = %s
        """, (group_id,))
        
        group_result = cursor.fetchone()
        if not group_result:
            cursor.close()
            conn.close()
            return {'can_join': False, 'reason': 'Group not found'}
        
        group_id_db, max_members, status = group_result
        
        if status != 'active':
            cursor.close()
            conn.close()
            return {'can_join': False, 'reason': f'Group is {status}'}
        
        # Check if user is already a member
        cursor.execute("""
            SELECT id FROM group_members 
            WHERE group_id = %s AND user_id = %s AND status = 'active'
        """, (group_id, user_id))
        
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {'can_join': False, 'reason': 'Already a member of this group'}
        
        # Check if group is full
        cursor.execute("""
            SELECT COUNT(*) FROM group_members 
            WHERE group_id = %s AND status = 'active'
        """, (group_id,))
        
        current_members = cursor.fetchone()[0]
        
        if current_members >= max_members:
            cursor.close()
            conn.close()
            return {'can_join': False, 'reason': 'Group is full'}
        
        cursor.close()
        conn.close()
        
        return {
            'can_join': True,
            'spots_available': max_members - current_members
        }
        
    except psycopg2.Error as e:
        print(f"Database error checking if user can join group: {e}")
        return {'can_join': False, 'reason': 'Database error'}
    except Exception as e:
        print(f"Unexpected error checking if user can join group: {e}")
        return {'can_join': False, 'reason': 'Unexpected error'} 