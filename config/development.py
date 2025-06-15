"""Development configuration module for Ajo application.

This module provides configuration settings optimized for development
environment with relaxed security settings and debug features enabled.
"""

from .base import BaseConfig


class DevelopmentConfig(BaseConfig):
    """Development environment configuration.
    
    Configuration class for development environment with debug mode enabled,
    relaxed security settings, and development-specific features.
    
    Attributes:
        DEBUG (bool): Enable debug mode for detailed error messages
        TESTING (bool): Disable testing mode
        LOG_LEVEL (str): Set logging level to DEBUG for verbose output
        SESSION_COOKIE_SECURE (bool): Allow non-HTTPS cookies in development
    """
    
    DEBUG = True
    TESTING = False
    
    # Development-specific settings
    LOG_LEVEL = 'DEBUG'
    
    # Allow less strict security in development
    SESSION_COOKIE_SECURE = False 