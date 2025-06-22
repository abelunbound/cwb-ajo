from werkzeug.security import generate_password_hash, check_password_hash
import re

# Session timeout (24 hours)
# SESSION_TIMEOUT = 24 * 60 * 60  # in seconds
SESSION_TIMEOUT = 0.5 * 60 * 60  # in seconds


# DEPRECATED: Mock user database - replaced with PostgreSQL in Task 12
# Kept for reference and migration purposes
USERS_DB = {
    'demo@example.com': {
        'password': generate_password_hash('password123'),
        'name': 'Abel',  # Match the name in your dashboard
        'created': '2025-01-01 00:00:00'
    },
    'admin@example.com': {
        'password': generate_password_hash('admin123'),
        'name': 'Admin User',
        'created': '2025-01-01 00:00:00'
    }
}

def validate_password_strength(password):
    """Validate password strength according to security requirements.
    
    Args:
        password (str): The password to validate
        
    Returns:
        dict: Dictionary with 'valid' boolean and 'errors' list
        
    Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter  
        - At least one number
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }

def register_user(email, password, password_confirm, name):
    """Register a new user with password validation using PostgreSQL.
    
    Args:
        email (str): User's email address
        password (str): User's password
        password_confirm (str): Password confirmation
        name (str): User's display name
        
    Returns:
        dict: Registration result with 'success' boolean and 'error' message
    """
    # Import here to avoid circular imports
    from functions.user_service import create_user
    
    # Validate password confirmation
    if password != password_confirm:
        return {'success': False, 'error': 'Passwords do not match'}
    
    # Validate password strength
    password_validation = validate_password_strength(password)
    if not password_validation['valid']:
        return {'success': False, 'error': '; '.join(password_validation['errors'])}
    
    # Create user in database
    password_hash = generate_password_hash(password)
    result = create_user(
        email=email,
        password_hash=password_hash,
        full_name=name,
        verification_status='unverified'
    )
    
    if result['success']:
        return {'success': True, 'error': None, 'user_id': result['user_id']}
    else:
        return {'success': False, 'error': result['error']}

def validate_user(email, password):
    """Validate user credentials using PostgreSQL and return user data if valid.
    
    Args:
        email (str): User's email address
        password (str): User's password
        
    Returns:
        dict or None: User data if valid, None if invalid
    """
    # Import here to avoid circular imports
    from functions.user_service import authenticate_user
    
    return authenticate_user(email, password)

# Backward compatibility functions for migration
def migrate_users_to_database():
    """Migrate users from in-memory USERS_DB to PostgreSQL database.
    
    Returns:
        dict: Migration result
    """
    from functions.user_service import migrate_demo_users
    return migrate_demo_users()

def get_user_profile(user_id):
    """Get user profile by ID.
    
    Args:
        user_id (int): User's database ID
        
    Returns:
        dict or None: User profile data
    """
    from functions.user_service import get_user_by_id
    return get_user_by_id(user_id)

def update_user_profile(user_id, **kwargs):
    """Update user profile fields.
    
    Args:
        user_id (int): User's database ID
        **kwargs: Fields to update
        
    Returns:
        dict: Update result
    """
    from functions.user_service import update_user_profile as update_profile
    return update_profile(user_id, **kwargs)