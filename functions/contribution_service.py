#!/usr/bin/env python3
"""
Contribution Tracking Service

This module provides functions for managing contributions in Ajo groups.
Handles contribution creation, payment tracking, status updates, and queries.
"""

import psycopg2
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from functions.database import get_ajo_db_connection


def record_contribution(group_id: int, user_id: int, amount: Decimal, 
                       due_date: date, payment_method: str = None) -> Dict[str, Any]:
    """
    Record a new contribution for a group member.
    
    Args:
        group_id: ID of the Ajo group
        user_id: ID of the contributing user
        amount: Contribution amount
        due_date: When the contribution is due
        payment_method: Optional payment method
        
    Returns:
        Dictionary with success status and contribution details
    """
    try:
        connection = get_ajo_db_connection()
        cursor = connection.cursor()
        
        # Validate group and user membership
        cursor.execute("""
            SELECT gm.id, ag.contribution_amount 
            FROM group_members gm
            JOIN ajo_groups ag ON gm.group_id = ag.id
            WHERE gm.group_id = %s AND gm.user_id = %s AND gm.status = 'active'
        """, (group_id, user_id))
        
        membership = cursor.fetchone()
        if not membership:
            return {
                'success': False,
                'error': 'User is not an active member of this group'
            }
        
        expected_amount = membership[1]
        if amount != expected_amount:
            return {
                'success': False,
                'error': f'Contribution amount must be {expected_amount}'
            }
        
        # Record the contribution
        cursor.execute("""
            INSERT INTO contributions (group_id, user_id, amount, due_date, payment_method, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, created_at
        """, (group_id, user_id, amount, due_date, payment_method, 'pending'))
        
        contribution_id, created_at = cursor.fetchone()
        connection.commit()
        
        return {
            'success': True,
            'contribution_id': contribution_id,
            'amount': amount,
            'due_date': due_date,
            'status': 'pending',
            'created_at': created_at
        }
        
    except psycopg2.Error as e:
        connection.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    finally:
        cursor.close()
        connection.close()


def mark_contribution_paid(contribution_id: int, transaction_id: str = None, 
                          paid_date: date = None) -> Dict[str, Any]:
    """
    Mark a contribution as paid.
    
    Args:
        contribution_id: ID of the contribution
        transaction_id: Optional transaction reference
        paid_date: Date payment was made (defaults to today)
        
    Returns:
        Dictionary with success status and updated details
    """
    try:
        connection = get_ajo_db_connection()
        cursor = connection.cursor()
        
        if paid_date is None:
            paid_date = date.today()
        
        # Update contribution status
        cursor.execute("""
            UPDATE contributions 
            SET status = 'paid', paid_date = %s, transaction_id = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND status = 'pending'
            RETURNING group_id, user_id, amount, due_date
        """, (paid_date, transaction_id, contribution_id))
        
        result = cursor.fetchone()
        if not result:
            return {
                'success': False,
                'error': 'Contribution not found or already processed'
            }
        
        group_id, user_id, amount, due_date = result
        connection.commit()
        
        return {
            'success': True,
            'contribution_id': contribution_id,
            'group_id': group_id,
            'user_id': user_id,
            'amount': amount,
            'due_date': due_date,
            'paid_date': paid_date,
            'transaction_id': transaction_id,
            'status': 'paid'
        }
        
    except psycopg2.Error as e:
        connection.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    finally:
        cursor.close()
        connection.close()


def get_user_contributions(user_id: int, group_id: int = None) -> List[Dict[str, Any]]:
    """
    Get all contributions for a specific user.
    
    Args:
        user_id: ID of the user
        group_id: Optional group ID to filter by specific group
        
    Returns:
        List of contribution records
    """
    try:
        connection = get_ajo_db_connection()
        cursor = connection.cursor()
        
        query = """
            SELECT c.id, c.group_id, ag.name as group_name, c.amount, 
                   c.due_date, c.paid_date, c.payment_method, c.transaction_id, 
                   c.status, c.created_at, c.updated_at
            FROM contributions c
            JOIN ajo_groups ag ON c.group_id = ag.id
            WHERE c.user_id = %s
        """
        params = [user_id]
        
        if group_id:
            query += " AND c.group_id = %s"
            params.append(group_id)
        
        query += " ORDER BY c.due_date DESC, c.created_at DESC"
        
        cursor.execute(query, params)
        contributions = cursor.fetchall()
        
        result = []
        for contrib in contributions:
            result.append({
                'id': contrib[0],
                'group_id': contrib[1],
                'group_name': contrib[2],
                'amount': contrib[3],
                'due_date': contrib[4],
                'paid_date': contrib[5],
                'payment_method': contrib[6],
                'transaction_id': contrib[7],
                'status': contrib[8],
                'created_at': contrib[9],
                'updated_at': contrib[10]
            })
        
        return result
        
    except psycopg2.Error as e:
        print(f"Database error in get_user_contributions: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def get_group_contributions(group_id: int, status: str = None) -> List[Dict[str, Any]]:
    """
    Get all contributions for a specific group.
    
    Args:
        group_id: ID of the group
        status: Optional status filter ('pending', 'paid', 'overdue', 'cancelled')
        
    Returns:
        List of contribution records with user details
    """
    try:
        connection = get_ajo_db_connection()
        cursor = connection.cursor()
        
        query = """
            SELECT c.id, c.user_id, u.full_name, u.email, c.amount, 
                   c.due_date, c.paid_date, c.payment_method, c.transaction_id, 
                   c.status, c.created_at, c.updated_at
            FROM contributions c
            JOIN users u ON c.user_id = u.id
            WHERE c.group_id = %s
        """
        params = [group_id]
        
        if status:
            query += " AND c.status = %s"
            params.append(status)
        
        query += " ORDER BY c.due_date DESC, u.full_name"
        
        cursor.execute(query, params)
        contributions = cursor.fetchall()
        
        result = []
        for contrib in contributions:
            result.append({
                'id': contrib[0],
                'user_id': contrib[1],
                'user_name': contrib[2],
                'user_email': contrib[3],
                'amount': contrib[4],
                'due_date': contrib[5],
                'paid_date': contrib[6],
                'payment_method': contrib[7],
                'transaction_id': contrib[8],
                'status': contrib[9],
                'created_at': contrib[10],
                'updated_at': contrib[11]
            })
        
        return result
        
    except psycopg2.Error as e:
        print(f"Database error in get_group_contributions: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def get_overdue_contributions(days_overdue: int = 0) -> List[Dict[str, Any]]:
    """
    Get all overdue contributions.
    
    Args:
        days_overdue: Minimum number of days overdue (default: 0 for any overdue)
        
    Returns:
        List of overdue contribution records
    """
    try:
        connection = get_ajo_db_connection()
        cursor = connection.cursor()
        
        cutoff_date = date.today() - timedelta(days=days_overdue)
        
        cursor.execute("""
            SELECT c.id, c.group_id, ag.name as group_name, c.user_id, u.full_name, 
                   u.email, c.amount, c.due_date, c.payment_method, c.status,
                   (CURRENT_DATE - c.due_date) as days_overdue
            FROM contributions c
            JOIN ajo_groups ag ON c.group_id = ag.id
            JOIN users u ON c.user_id = u.id
            WHERE c.status = 'pending' AND c.due_date <= %s
            ORDER BY c.due_date ASC, ag.name, u.full_name
        """, (cutoff_date,))
        
        contributions = cursor.fetchall()
        
        result = []
        for contrib in contributions:
            result.append({
                'id': contrib[0],
                'group_id': contrib[1],
                'group_name': contrib[2],
                'user_id': contrib[3],
                'user_name': contrib[4],
                'user_email': contrib[5],
                'amount': contrib[6],
                'due_date': contrib[7],
                'payment_method': contrib[8],
                'status': contrib[9],
                'days_overdue': contrib[10]
            })
        
        return result
        
    except psycopg2.Error as e:
        print(f"Database error in get_overdue_contributions: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def update_overdue_contributions() -> Dict[str, Any]:
    """
    Update pending contributions that are past due to 'overdue' status.
    
    Returns:
        Dictionary with update results
    """
    try:
        connection = get_ajo_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            UPDATE contributions 
            SET status = 'overdue', updated_at = CURRENT_TIMESTAMP
            WHERE status = 'pending' AND due_date < CURRENT_DATE
            RETURNING id
        """)
        
        updated_ids = [row[0] for row in cursor.fetchall()]
        connection.commit()
        
        return {
            'success': True,
            'updated_count': len(updated_ids),
            'updated_ids': updated_ids
        }
        
    except psycopg2.Error as e:
        connection.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    finally:
        cursor.close()
        connection.close()


def get_contribution_summary(group_id: int) -> Dict[str, Any]:
    """
    Get contribution summary for a group.
    
    Args:
        group_id: ID of the group
        
    Returns:
        Dictionary with contribution statistics
    """
    try:
        connection = get_ajo_db_connection()
        cursor = connection.cursor()
        
        # Get overall statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_contributions,
                COUNT(CASE WHEN status = 'paid' THEN 1 END) as paid_contributions,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_contributions,
                COUNT(CASE WHEN status = 'overdue' THEN 1 END) as overdue_contributions,
                COALESCE(SUM(CASE WHEN status = 'paid' THEN amount ELSE 0 END), 0) as total_paid,
                COALESCE(SUM(CASE WHEN status = 'pending' THEN amount ELSE 0 END), 0) as total_pending,
                COALESCE(SUM(CASE WHEN status = 'overdue' THEN amount ELSE 0 END), 0) as total_overdue
            FROM contributions 
            WHERE group_id = %s
        """, (group_id,))
        
        stats = cursor.fetchone()
        
        # Get recent activity
        cursor.execute("""
            SELECT c.id, u.full_name, c.amount, c.status, c.due_date, c.paid_date
            FROM contributions c
            JOIN users u ON c.user_id = u.id
            WHERE c.group_id = %s
            ORDER BY COALESCE(c.paid_date, c.updated_at, c.created_at) DESC
            LIMIT 10
        """, (group_id,))
        
        recent_activity = []
        for activity in cursor.fetchall():
            recent_activity.append({
                'id': activity[0],
                'user_name': activity[1],
                'amount': activity[2],
                'status': activity[3],
                'due_date': activity[4],
                'paid_date': activity[5]
            })
        
        return {
            'group_id': group_id,
            'total_contributions': stats[0],
            'paid_contributions': stats[1],
            'pending_contributions': stats[2],
            'overdue_contributions': stats[3],
            'total_paid': stats[4],
            'total_pending': stats[5],
            'total_overdue': stats[6],
            'recent_activity': recent_activity
        }
        
    except psycopg2.Error as e:
        print(f"Database error in get_contribution_summary: {e}")
        return {
            'group_id': group_id,
            'error': f'Database error: {str(e)}'
        }
    finally:
        cursor.close()
        connection.close()


def cancel_contribution(contribution_id: int, reason: str = None) -> Dict[str, Any]:
    """
    Cancel a pending contribution.
    
    Args:
        contribution_id: ID of the contribution to cancel
        reason: Optional reason for cancellation
        
    Returns:
        Dictionary with success status
    """
    try:
        connection = get_ajo_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            UPDATE contributions 
            SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND status IN ('pending', 'overdue')
            RETURNING group_id, user_id, amount, due_date
        """, (contribution_id,))
        
        result = cursor.fetchone()
        if not result:
            return {
                'success': False,
                'error': 'Contribution not found or cannot be cancelled'
            }
        
        group_id, user_id, amount, due_date = result
        connection.commit()
        
        return {
            'success': True,
            'contribution_id': contribution_id,
            'group_id': group_id,
            'user_id': user_id,
            'amount': amount,
            'due_date': due_date,
            'status': 'cancelled',
            'reason': reason
        }
        
    except psycopg2.Error as e:
        connection.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    finally:
        cursor.close()
        connection.close()


def bulk_create_contributions(group_id: int, due_date: date, 
                            exclude_user_ids: List[int] = None) -> Dict[str, Any]:
    """
    Create contributions for all active group members.
    
    Args:
        group_id: ID of the group
        due_date: Due date for all contributions
        exclude_user_ids: Optional list of user IDs to exclude
        
    Returns:
        Dictionary with creation results
    """
    try:
        connection = get_ajo_db_connection()
        cursor = connection.cursor()
        
        # Get group details and active members
        cursor.execute("""
            SELECT ag.contribution_amount, array_agg(gm.user_id) as member_ids
            FROM ajo_groups ag
            JOIN group_members gm ON ag.id = gm.group_id
            WHERE ag.id = %s AND gm.status = 'active'
            GROUP BY ag.id, ag.contribution_amount
        """, (group_id,))
        
        result = cursor.fetchone()
        if not result:
            return {
                'success': False,
                'error': 'Group not found or has no active members'
            }
        
        contribution_amount, member_ids = result
        
        # Filter out excluded users
        if exclude_user_ids:
            member_ids = [uid for uid in member_ids if uid not in exclude_user_ids]
        
        if not member_ids:
            return {
                'success': False,
                'error': 'No members to create contributions for'
            }
        
        # Create contributions for all members
        created_contributions = []
        for user_id in member_ids:
            cursor.execute("""
                INSERT INTO contributions (group_id, user_id, amount, due_date, status)
                VALUES (%s, %s, %s, %s, 'pending')
                RETURNING id
            """, (group_id, user_id, contribution_amount, due_date))
            
            contribution_id = cursor.fetchone()[0]
            created_contributions.append({
                'id': contribution_id,
                'user_id': user_id,
                'amount': contribution_amount,
                'due_date': due_date
            })
        
        connection.commit()
        
        return {
            'success': True,
            'group_id': group_id,
            'created_count': len(created_contributions),
            'contributions': created_contributions
        }
        
    except psycopg2.Error as e:
        connection.rollback()
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    finally:
        cursor.close()
        connection.close()