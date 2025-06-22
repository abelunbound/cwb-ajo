from werkzeug.security import generate_password_hash, check_password_hash
import re

# Session timeout (24 hours)
# SESSION_TIMEOUT = 24 * 60 * 60  # in seconds
SESSION_TIMEOUT = 0.5 * 60 * 60  # in seconds


# Mock user database - replace with real database in production
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
    """Register a new user with password validation.
    
    Args:
        email (str): User's email address
        password (str): User's password
        password_confirm (str): Password confirmation
        name (str): User's display name
        
    Returns:
        dict: Registration result with 'success' boolean and 'error' message
    """
    # Check if user already exists
    if email in USERS_DB:
        return {'success': False, 'error': 'User already exists'}
    
    # Validate password confirmation
    if password != password_confirm:
        return {'success': False, 'error': 'Passwords do not match'}
    
    # Validate password strength
    password_validation = validate_password_strength(password)
    if not password_validation['valid']:
        return {'success': False, 'error': '; '.join(password_validation['errors'])}
    
    # Create new user
    USERS_DB[email] = {
        'password': generate_password_hash(password),
        'name': name,
        'created': '2025-01-01 00:00:00'  # TODO: Use actual timestamp
    }
    
    return {'success': True, 'error': None}

def validate_user(email, password):
    """Validate user credentials and return user data if valid.
    
    Args:
        email (str): User's email address
        password (str): User's password
        
    Returns:
        dict or None: User data if valid, None if invalid
    """
    # Check if user exists
    if email not in USERS_DB:
        return None
    
    # Check password
    if not check_password_hash(USERS_DB[email]['password'], password):
        return None
    
    # Return user info (excluding password)
    return {
        'email': email,
        'name': USERS_DB[email]['name']
    }