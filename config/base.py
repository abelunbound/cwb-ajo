"""Base configuration module for Ajo application.

This module provides the BaseConfig class that serves as the foundation
for all environment-specific configuration classes.
"""

import os
from dotenv import load_dotenv


class BaseConfig:
    """Base configuration class with common settings.
    
    This class provides default configuration values and methods
    that are inherited by environment-specific configuration classes.
    All configuration values are loaded from environment variables.
    
    Attributes:
        DB_NAME (str): Database name from environment variable
        DB_USER (str): Database user from environment variable  
        DB_PASSWORD (str): Database password from environment variable
        DB_HOST (str): Database host from environment variable
        DB_PORT (str): Database port from environment variable
        SECRET_KEY (str): Application secret key from environment variable
        DEBUG (bool): Debug mode flag
        TESTING (bool): Testing mode flag
    """
    
    def __init__(self):
        """Initialize configuration by loading environment variables."""
        # Load environment variables from .env file
        load_dotenv()
    
    # Database Configuration
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER') 
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT', '5432')
    
    # Application Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    @classmethod
    def validate_config(cls):
        """Validate that all required environment variables are set.
        
        Checks that all critical environment variables required for
        database connectivity are present and not empty.
        
        Returns:
            bool: True if all required variables are present
            
        Raises:
            ValueError: If any required environment variables are missing
        """
        required_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST']
        missing_vars = []
        
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True 