"""
User Service Module for Ajo Platform

This module provides database operations for user management,
replacing the in-memory USERS_DB with PostgreSQL storage.
"""

import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .database import get_ajo_db_connection


def create_user(email, password_hash, full_name, phone_number=None, 
                bank_account_details=None, verification_status='unverified',
                preferred_payment_method='bank_transfer'):
    """Create a new user in the database.
    
    Args:
        email (str): User's email address
        password_hash (str): Hashed password
        full_name (str): User's full name
        phone_number (str, optional): User's phone number
        bank_account_details (str, optional): Encrypted bank details
        verification_status (str): Verification status (default: 'unverified')
        preferred_payment_method (str): Preferred payment method
        
    Returns:
        dict: Result with 'success' boolean and 'user_id' or 'error'
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return {'success': False, 'error': 'Database connection failed'}
            
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {'success': False, 'error': 'User already exists'}
        
        # Insert new user
        insert_query = """
            INSERT INTO users (email, password_hash, full_name, phone_number, 
                             bank_account_details, verification_status, preferred_payment_method)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        
        cursor.execute(insert_query, (
            email, password_hash, full_name, phone_number,
            bank_account_details, verification_status, preferred_payment_method
        ))
        
        user_id = cursor.fetchone()[0]
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {'success': True, 'user_id': user_id}
        
    except psycopg2.Error as e:
        return {'success': False, 'error': f'Database error: {str(e)}'}


def get_user_by_email(email):
    """Retrieve user by email address.
    
    Args:
        email (str): User's email address
        
    Returns:
        dict or None: User data if found, None if not found
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return None
            
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, email, password_hash, full_name, phone_number,
                   verification_status, preferred_payment_method, created_at
            FROM users WHERE email = %s
        """, (email,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'email': result[1],
                'password_hash': result[2],
                'full_name': result[3],
                'phone_number': result[4],
                'verification_status': result[5],
                'preferred_payment_method': result[6],
                'created_at': result[7]
            }
        return None
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None


def get_user_by_id(user_id):
    """Retrieve user by ID.
    
    Args:
        user_id (int): User's ID
        
    Returns:
        dict or None: User data if found, None if not found
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return None
            
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, email, full_name, phone_number, bank_account_details,
                   credit_score, verification_status, preferred_payment_method, created_at
            FROM users WHERE id = %s
        """, (user_id,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'email': result[1],
                'full_name': result[2],
                'phone_number': result[3],
                'bank_account_details': result[4],
                'credit_score': result[5],
                'verification_status': result[6],
                'preferred_payment_method': result[7],
                'created_at': result[8]
            }
        return None
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None


def update_user_profile(user_id, **kwargs):
    """Update user profile fields.
    
    Args:
        user_id (int): User's ID
        **kwargs: Fields to update (phone_number, bank_account_details, etc.)
        
    Returns:
        dict: Result with 'success' boolean and 'error' if applicable
    """
    try:
        conn = get_ajo_db_connection()
        if not conn:
            return {'success': False, 'error': 'Database connection failed'}
            
        cursor = conn.cursor()
        
        # Build dynamic update query
        allowed_fields = [
            'phone_number', 'bank_account_details', 'credit_score',
            'verification_status', 'preferred_payment_method', 'full_name'
        ]
        
        update_fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = %s")
                values.append(value)
        
        if not update_fields:
            return {'success': False, 'error': 'No valid fields to update'}
        
        # Add updated_at timestamp
        update_fields.append("updated_at = %s")
        values.append(datetime.now())
        values.append(user_id)
        
        update_query = f"""
            UPDATE users 
            SET {', '.join(update_fields)}
            WHERE id = %s
        """
        
        cursor.execute(update_query, values)
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return {'success': True}
        
    except psycopg2.Error as e:
        return {'success': False, 'error': f'Database error: {str(e)}'}


def authenticate_user(email, password):
    """Authenticate user with email and password.
    
    Args:
        email (str): User's email address
        password (str): Plain text password
        
    Returns:
        dict or None: User data (without password) if valid, None if invalid
    """
    user = get_user_by_email(email)
    if not user:
        return None
        
    # Check password
    if not check_password_hash(user['password_hash'], password):
        return None
    
    # Return user info (excluding password hash)
    return {
        'id': user['id'],
        'email': user['email'],
        'name': user['full_name'],  # For compatibility with existing code
        'full_name': user['full_name'],
        'phone_number': user['phone_number'],
        'verification_status': user['verification_status'],
        'preferred_payment_method': user['preferred_payment_method']
    }


def migrate_demo_users():
    """Migrate demo users from in-memory to database.
    
    Returns:
        dict: Migration result with success status and details
    """
    demo_users = [
        {
            'email': 'demo@example.com',
            'password': 'password123',
            'full_name': 'Abel',
            'verification_status': 'verified'
        },
        {
            'email': 'admin@example.com', 
            'password': 'admin123',
            'full_name': 'Admin User',
            'verification_status': 'verified'
        }
    ]
    
    results = []
    
    for user_data in demo_users:
        # Check if user already exists
        existing_user = get_user_by_email(user_data['email'])
        if existing_user:
            results.append({
                'email': user_data['email'],
                'status': 'already_exists',
                'user_id': existing_user['id']
            })
            continue
        
        # Create user
        password_hash = generate_password_hash(user_data['password'])
        result = create_user(
            email=user_data['email'],
            password_hash=password_hash,
            full_name=user_data['full_name'],
            verification_status=user_data['verification_status']
        )
        
        if result['success']:
            results.append({
                'email': user_data['email'],
                'status': 'created',
                'user_id': result['user_id']
            })
        else:
            results.append({
                'email': user_data['email'],
                'status': 'failed',
                'error': result['error']
            })
    
    return {
        'success': True,
        'migrated_users': results
    } 