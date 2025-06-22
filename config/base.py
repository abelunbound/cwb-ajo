"""Base configuration module for Ajo application.

This module provides the BaseConfig class that serves as the foundation
for all environment-specific configuration classes.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file in root directory
load_dotenv()


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
        pass
    
    # Database Configuration - loaded dynamically
    @property
    def DB_NAME(self):
        return os.getenv('DB_NAME')
    
    @property
    def DB_USER(self):
        return os.getenv('DB_USER')
    
    @property
    def DB_PASSWORD(self):
        return os.getenv('DB_PASSWORD')
    
    @property
    def DB_HOST(self):
        return os.getenv('DB_HOST')
    
    @property
    def DB_PORT(self):
        return os.getenv('DB_PORT', '5432')
    
    # Ajo Database Configuration - loaded dynamically
    @property
    def AJO_DB_NAME(self):
        return os.getenv('AJO_DB_NAME')
    
    @property
    def AJO_DB_USER(self):
        return os.getenv('AJO_DB_USER')
    
    @property
    def AJO_DB_PASSWORD(self):
        return os.getenv('AJO_DB_PASSWORD')
    
    @property
    def AJO_DB_HOST(self):
        return os.getenv('AJO_DB_HOST')
    
    @property
    def AJO_DB_PORT(self):
        return os.getenv('AJO_DB_PORT', '5432')
    
    # Application Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    def validate_config(self):
        """Validate that all required environment variables are set.
        
        Checks that all critical environment variables required for
        database connectivity are present and not empty.
        
        Returns:
            bool: True if all required variables are present
            
        Raises:
            ValueError: If any required environment variables are missing
        """
        # CWB Database (finhealth) - required
        cwb_required_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST']
        missing_cwb_vars = []
        
        for var in cwb_required_vars:
            if not getattr(self, var):
                missing_cwb_vars.append(var)
        
        # Ajo Database - required for Ajo functionality
        ajo_required_vars = ['AJO_DB_NAME', 'AJO_DB_USER', 'AJO_DB_PASSWORD', 'AJO_DB_HOST']
        missing_ajo_vars = []
        
        for var in ajo_required_vars:
            if not getattr(self, var):
                missing_ajo_vars.append(var)
        
        # Report missing variables
        all_missing = missing_cwb_vars + missing_ajo_vars
        if all_missing:
            raise ValueError(f"Missing required environment variables: {', '.join(all_missing)}")
        
        return True 