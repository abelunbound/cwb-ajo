from werkzeug.security import generate_password_hash, check_password_hash

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

def validate_user(email, password):
    """Validate user credentials and return user data if valid"""
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