#!/usr/bin/env python3
"""
Payment Distribution Service

This module provides functions for managing payment distributions in Ajo groups.
Handles distribution creation, payment tracking, status updates, and queries.
"""

import psycopg2
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from functions.database import get_ajo_db_connection


def create_distribution(group_id: int, recipient_id: int, amount: Decimal,
                       distribution_date: date = None, notes: str = None) -> Dict[str, Any]:
    """
    Create a new distribution record for a group member.
    
    Args:
        group_id: ID of the Ajo group
        recipient_id: ID of the recipient user
        amount: Distribution amount
        distribution_date: Date of distribution (defaults to today)
        notes: Optional notes about the distribution
        
    Returns:
        Dictionary with success status and distribution details
    """
    try:
        connection = get_ajo_db_connection()
        cursor = connection.cursor()
        
        if distribution_date is None:
            distribution_date = date.today()
        
        # Validate group and recipient membership
        cursor.execute("""
            SELECT gm.id, gm.role, gm.payment_position, ag.contribution_amount
            FROM group_members gm
            JOIN ajo_groups ag ON gm.group_id = ag.id
            WHERE gm.group_id = %s AND gm.user_id = %s AND gm.status = 'active'
        """, (group_id, recipient_id))
        
        membership = cursor.fetchone()
        if not membership:
            return {
                'success': False,
                'error': 'Recipient is not an active member of this group'
            }
        
        member_id, role, payment_position, group_contribution_amount = membership
        
        # Validate distribution amount (should typically match total contributions collected)
        cursor.execute("""
            SELECT COUNT(*) as member_count
            FROM group_members 
            WHERE group_id = %s AND status = 'active'
        """, (group_id,))
        
        member_count = cursor.fetchone()[0]
        expected_amount = group_contribution_amount * member_count
        
        if amount > expected_amount:
            return {
                'success': False,
                'error': f'Distribution amount ({amount}) exceeds maximum possible ({expected_amount})'
            }
        
        # Create the distribution record
        cursor.execute("""
            INSERT INTO distributions (group_id, recipient_id, amount, distribution_date, status, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, created_at
        """, (group_id, recipient_id, amount, distribution_date, 'pending', notes))
        
        distribution_id, created_at = cursor.fetchone()
        connection.commit()
        
        return {
            'success': True,
            'distribution_id': distribution_id,
            'group_id': group_id,
            'recipient_id': recipient_id,
            'amount': amount,
            'distribution_date': distribution_date,
            'status': 'pending',
            'payment_position': payment_position,
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


def complete_distribution(distribution_id: int, transaction_id: str = None,
                         completion_date: date = None) -> Dict[str, Any]:
    """
    Mark a distribution as completed.
    
    Args:
        distribution_id: ID of the distribution
        transaction_id: Optional transaction reference
        completion_date: Date distribution was completed (defaults to today)
        
    Returns:
        Dictionary with success status and updated details
    """
    try:
        connection = get_ajo_db_connection()
        cursor = connection.cursor()
        
        if completion_date is None:
            completion_date = date.today()
        
        # Update distribution status
        cursor.execute("""
            UPDATE distributions 
            SET status = 'completed', transaction_id = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND status = 'pending'
            RETURNING group_id, recipient_id, amount, distribution_date
        """, (transaction_id, distribution_id))
        
        result = cursor.fetchone()
        if not result:
            return {
                'success': False,
                'error': 'Distribution not found or already processed'
            }
        
        group_id, recipient_id, amount, distribution_date = result
        connection.commit()
        
        return {
            'success': True,
            'distribution_id': distribution_id,
            'group_id': group_id,
            'recipient_id': recipient_id,
            'amount': amount,
            'distribution_date': distribution_date,
            'completion_date': completion_date,
            'transaction_id': transaction_id,
            'status': 'completed'
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


def fail_distribution(distribution_id: int, reason: str = None) -> Dict[str, Any]:
    """
    Mark a distribution as failed.
    
    Args:
        distribution_id: ID of the distribution
        reason: Reason for failure
        
    Returns:
        Dictionary with success status and updated details
    """
    try:
        connection = get_ajo_db_connection()
        cursor = connection.cursor()
        
        # Update distribution status and add reason to notes
        cursor.execute("""
            UPDATE distributions 
            SET status = 'failed', 
                notes = CASE 
                    WHEN notes IS NULL OR notes = '' THEN %s
                    ELSE notes || ' | FAILURE: ' || %s
                END,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND status = 'pending'
            RETURNING group_id, recipient_id, amount, distribution_date
        """, (f'FAILURE: {reason}' if reason else 'FAILURE: Unspecified', reason or 'Unspecified', distribution_id))
        
        result = cursor.fetchone()
        if not result:
            return {
                'success': False,
                'error': 'Distribution not found or already processed'
            }
        
        group_id, recipient_id, amount, distribution_date = result
        connection.commit()
        
        return {
            'success': True,
            'distribution_id': distribution_id,
            'group_id': group_id,
            'recipient_id': recipient_id,
            'amount': amount,
            'distribution_date': distribution_date,
            'status': 'failed',
            'failure_reason': reason
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


def get_group_distributions(group_id: int, status: str = None) -> List[Dict[str, Any]]:
    """
    Get all distributions for a specific group.
    
    Args:
        group_id: ID of the group
        status: Optional status filter ('pending', 'completed', 'failed')
        
    Returns:
        List of distribution records with recipient details
    """
    try:
        connection = get_ajo_db_connection()
        cursor = connection.cursor()
        
        query = """
            SELECT d.id, d.recipient_id, u.full_name, u.email, d.amount, 
                   d.distribution_date, d.transaction_id, d.status, d.notes,
                   gm.payment_position, d.created_at, d.updated_at
            FROM distributions d
            JOIN users u ON d.recipient_id = u.id
            LEFT JOIN group_members gm ON d.group_id = gm.group_id AND d.recipient_id = gm.user_id
            WHERE d.group_id = %s
        """
        params = [group_id]
        
        if status:
            query += " AND d.status = %s"
            params.append(status)
        
        query += " ORDER BY d.distribution_date DESC, gm.payment_position"
        
        cursor.execute(query, params)
        distributions = cursor.fetchall()
        
        result = []
        for dist in distributions:
            result.append({
                'id': dist[0],
                'recipient_id': dist[1],
                'recipient_name': dist[2],
                'recipient_email': dist[3],
                'amount': dist[4],
                'distribution_date': dist[5],
                'transaction_id': dist[6],
                'status': dist[7],
                'notes': dist[8],
                'payment_position': dist[9],
                'created_at': dist[10],
                'updated_at': dist[11]
            })
        
        return result
        
    except psycopg2.Error as e:
        print(f"Database error in get_group_distributions: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def get_user_distributions(user_id: int, group_id: int = None) -> List[Dict[str, Any]]:
    """
    Get all distributions received by a specific user.
    
    Args:
        user_id: ID of the user
        group_id: Optional group ID to filter by specific group
        
    Returns:
        List of distribution records
    """
    try:
        connection = get_ajo_db_connection()
        cursor = connection.cursor()
        
        query = """
            SELECT d.id, d.group_id, ag.name as group_name, d.amount, 
                   d.distribution_date, d.transaction_id, d.status, d.notes,
                   d.created_at, d.updated_at
            FROM distributions d
            JOIN ajo_groups ag ON d.group_id = ag.id
            WHERE d.recipient_id = %s
        """
        params = [user_id]
        
        if group_id:
            query += " AND d.group_id = %s"
            params.append(group_id)
        
        query += " ORDER BY d.distribution_date DESC, d.created_at DESC"
        
        cursor.execute(query, params)
        distributions = cursor.fetchall()
        
        result = []
        for dist in distributions:
            result.append({
                'id': dist[0],
                'group_id': dist[1],
                'group_name': dist[2],
                'amount': dist[3],
                'distribution_date': dist[4],
                'transaction_id': dist[5],
                'status': dist[6],
                'notes': dist[7],
                'created_at': dist[8],
                'updated_at': dist[9]
            })
        
        return result
        
    except psycopg2.Error as e:
        print(f"Database error in get_user_distributions: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def get_distribution_summary(group_id: int) -> Dict[str, Any]:
    """
    Get distribution summary for a group.
    
    Args:
        group_id: ID of the group
        
    Returns:
        Dictionary with distribution statistics
    """
    try:
        connection = get_ajo_db_connection()
        cursor = connection.cursor()
        
        # Get overall statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_distributions,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_distributions,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_distributions,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_distributions,
                COALESCE(SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END), 0) as total_distributed,
                COALESCE(SUM(CASE WHEN status = 'pending' THEN amount ELSE 0 END), 0) as total_pending,
                COALESCE(AVG(CASE WHEN status = 'completed' THEN amount END), 0) as avg_distribution
            FROM distributions 
            WHERE group_id = %s
        """, (group_id,))
        
        stats = cursor.fetchone()
        
        # Get recent distributions
        cursor.execute("""
            SELECT d.id, u.full_name, d.amount, d.status, d.distribution_date, gm.payment_position
            FROM distributions d
            JOIN users u ON d.recipient_id = u.id
            LEFT JOIN group_members gm ON d.group_id = gm.group_id AND d.recipient_id = gm.user_id
            WHERE d.group_id = %s
            ORDER BY d.distribution_date DESC, d.created_at DESC
            LIMIT 10
        """, (group_id,))
        
        recent_distributions = []
        for dist in cursor.fetchall():
            recent_distributions.append({
                'id': dist[0],
                'recipient_name': dist[1],
                'amount': dist[2],
                'status': dist[3],
                'distribution_date': dist[4],
                'payment_position': dist[5]
            })
        
        return {
            'group_id': group_id,
            'total_distributions': stats[0],
            'completed_distributions': stats[1],
            'pending_distributions': stats[2],
            'failed_distributions': stats[3],
            'total_distributed': stats[4],
            'total_pending': stats[5],
            'avg_distribution': stats[6],
            'recent_distributions': recent_distributions
        }
        
    except psycopg2.Error as e:
        print(f"Database error in get_distribution_summary: {e}")
        return {
            'group_id': group_id,
            'error': f'Database error: {str(e)}'
        }
    finally:
        cursor.close()
        connection.close()


def get_next_recipient(group_id: int) -> Dict[str, Any]:
    """
    Get the next member in line to receive a distribution based on payment position.
    
    Args:
        group_id: ID of the group
        
    Returns:
        Dictionary with next recipient details or None if cycle complete
    """
    try:
        connection = get_ajo_db_connection()
        cursor = connection.cursor()
        
        # Get all active members with their payment positions
        cursor.execute("""
            SELECT gm.user_id, u.full_name, gm.payment_position
            FROM group_members gm
            JOIN users u ON gm.user_id = u.id
            WHERE gm.group_id = %s AND gm.status = 'active'
            ORDER BY gm.payment_position
        """, (group_id,))
        
        members = cursor.fetchall()
        if not members:
            return {
                'success': False,
                'error': 'No active members found in group'
            }
        
        # Get members who have already received distributions
        cursor.execute("""
            SELECT DISTINCT recipient_id
            FROM distributions
            WHERE group_id = %s AND status = 'completed'
        """, (group_id,))
        
        completed_recipients = {row[0] for row in cursor.fetchall()}
        
        # Find next recipient who hasn't received a distribution yet
        for user_id, full_name, payment_position in members:
            if user_id not in completed_recipients:
                return {
                    'success': True,
                    'user_id': user_id,
                    'full_name': full_name,
                    'payment_position': payment_position,
                    'is_next': True
                }
        
        # If everyone has received, start new cycle with first member
        first_member = members[0]
        return {
            'success': True,
            'user_id': first_member[0],
            'full_name': first_member[1],
            'payment_position': first_member[2],
            'is_next': True,
            'new_cycle': True
        }
        
    except psycopg2.Error as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    finally:
        cursor.close()
        connection.close()


def calculate_distribution_amount(group_id: int, period_start: date = None, 
                                period_end: date = None) -> Dict[str, Any]:
    """
    Calculate the amount available for distribution based on contributions.
    
    Args:
        group_id: ID of the group
        period_start: Start date for contribution period
        period_end: End date for contribution period
        
    Returns:
        Dictionary with distribution calculation details
    """
    try:
        connection = get_ajo_db_connection()
        cursor = connection.cursor()
        
        # If no period specified, use current month
        if period_start is None:
            today = date.today()
            period_start = date(today.year, today.month, 1)
        
        if period_end is None:
            period_end = date.today()
        
        # First get group info and member count
        cursor.execute("""
            SELECT ag.contribution_amount, COUNT(gm.user_id) as active_members
            FROM ajo_groups ag
            LEFT JOIN group_members gm ON ag.id = gm.group_id AND gm.status = 'active'
            WHERE ag.id = %s
            GROUP BY ag.id, ag.contribution_amount
        """, (group_id,))
        
        group_result = cursor.fetchone()
        if not group_result:
            return {
                'success': False,
                'error': 'Group not found'
            }
        
        contribution_amount, active_members = group_result
        
        # Then get contribution statistics for the period
        cursor.execute("""
            SELECT 
                COUNT(*) as total_contributions,
                COUNT(CASE WHEN status = 'paid' THEN 1 END) as paid_contributions,
                COALESCE(SUM(CASE WHEN status = 'paid' THEN amount ELSE 0 END), 0) as total_collected
            FROM contributions
            WHERE group_id = %s AND due_date >= %s AND due_date <= %s
        """, (group_id, period_start, period_end))
        
        contrib_result = cursor.fetchone()
        if contrib_result:
            total_contributions, paid_contributions, total_collected = contrib_result
        else:
            total_contributions, paid_contributions, total_collected = 0, 0, Decimal('0')
        
        # Calculate expected total (all members should contribute)
        expected_total = contribution_amount * active_members if active_members else 0
        
        return {
            'success': True,
            'group_id': group_id,
            'period_start': period_start,
            'period_end': period_end,
            'total_contributions': total_contributions or 0,
            'paid_contributions': paid_contributions or 0,
            'total_collected': total_collected,
            'expected_total': expected_total,
            'available_for_distribution': total_collected,
            'contribution_rate': (paid_contributions / active_members * 100) if active_members > 0 else 0,
            'active_members': active_members or 0
        }
        
    except psycopg2.Error as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    finally:
        cursor.close()
        connection.close()


def get_distribution_history(group_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get complete distribution history for a group.
    
    Args:
        group_id: ID of the group
        limit: Maximum number of records to return
        
    Returns:
        List of distribution records with full details
    """
    try:
        connection = get_ajo_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT d.id, d.recipient_id, u.full_name, u.email, d.amount, 
                   d.distribution_date, d.transaction_id, d.status, d.notes,
                   gm.payment_position, d.created_at, d.updated_at,
                   ag.name as group_name, ag.contribution_amount
            FROM distributions d
            JOIN users u ON d.recipient_id = u.id
            JOIN ajo_groups ag ON d.group_id = ag.id
            LEFT JOIN group_members gm ON d.group_id = gm.group_id AND d.recipient_id = gm.user_id
            WHERE d.group_id = %s
            ORDER BY d.distribution_date DESC, d.created_at DESC
            LIMIT %s
        """, (group_id, limit))
        
        distributions = cursor.fetchall()
        
        result = []
        for dist in distributions:
            result.append({
                'id': dist[0],
                'recipient_id': dist[1],
                'recipient_name': dist[2],
                'recipient_email': dist[3],
                'amount': dist[4],
                'distribution_date': dist[5],
                'transaction_id': dist[6],
                'status': dist[7],
                'notes': dist[8],
                'payment_position': dist[9],
                'created_at': dist[10],
                'updated_at': dist[11],
                'group_name': dist[12],
                'group_contribution_amount': dist[13]
            })
        
        return result
        
    except psycopg2.Error as e:
        print(f"Database error in get_distribution_history: {e}")
        return []
    finally:
        cursor.close()
        connection.close()


def validate_distribution_eligibility(group_id: int, recipient_id: int) -> Dict[str, Any]:
    """
    Validate if a member is eligible to receive a distribution.
    
    Args:
        group_id: ID of the group
        recipient_id: ID of the potential recipient
        
    Returns:
        Dictionary with eligibility status and details
    """
    try:
        connection = get_ajo_db_connection()
        cursor = connection.cursor()
        
        # Check if user is an active member
        cursor.execute("""
            SELECT gm.id, gm.role, gm.payment_position, gm.status
            FROM group_members gm
            WHERE gm.group_id = %s AND gm.user_id = %s
        """, (group_id, recipient_id))
        
        membership = cursor.fetchone()
        if not membership:
            return {
                'eligible': False,
                'reason': 'User is not a member of this group'
            }
        
        member_id, role, payment_position, status = membership
        if status != 'active':
            return {
                'eligible': False,
                'reason': f'User membership status is {status}, not active'
            }
        
        # Check if user has recent distributions (to prevent double-dipping)
        cursor.execute("""
            SELECT COUNT(*) as recent_distributions
            FROM distributions
            WHERE group_id = %s AND recipient_id = %s 
            AND distribution_date >= CURRENT_DATE - INTERVAL '30 days'
            AND status = 'completed'
        """, (group_id, recipient_id))
        
        recent_count = cursor.fetchone()[0]
        
        # Check user's contribution status
        cursor.execute("""
            SELECT 
                COUNT(*) as total_contributions,
                COUNT(CASE WHEN status = 'paid' THEN 1 END) as paid_contributions
            FROM contributions
            WHERE group_id = %s AND user_id = %s
            AND due_date >= CURRENT_DATE - INTERVAL '90 days'
        """, (group_id, recipient_id))
        
        contrib_total, contrib_paid = cursor.fetchone()
        contribution_rate = (contrib_paid / contrib_total * 100) if contrib_total > 0 else 0
        
        return {
            'eligible': True,
            'member_id': member_id,
            'role': role,
            'payment_position': payment_position,
            'recent_distributions': recent_count,
            'contribution_rate': contribution_rate,
            'total_contributions': contrib_total,
            'paid_contributions': contrib_paid,
            'warnings': [
                'User has received distribution recently' if recent_count > 0 else None,
                'Low contribution rate' if contribution_rate < 80 else None
            ]
        }
        
    except psycopg2.Error as e:
        return {
            'eligible': False,
            'reason': f'Database error: {str(e)}'
        }
    finally:
        cursor.close()
        connection.close()