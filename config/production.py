"""Production configuration module for Ajo application.

This module provides configuration settings optimized for production
environment with strict security settings and performance optimizations.
"""

from .base import BaseConfig


class ProductionConfig(BaseConfig):
    """Production environment configuration.
    
    Configuration class for production environment with strict security
    settings, performance optimizations, and production-grade features.
    
    Attributes:
        DEBUG (bool): Disable debug mode for security
        TESTING (bool): Disable testing mode
        LOG_LEVEL (str): Set logging level to INFO for production
        SESSION_COOKIE_SECURE (bool): Require HTTPS for cookies
        SESSION_COOKIE_HTTPONLY (bool): Prevent JavaScript access to cookies
        SESSION_COOKIE_SAMESITE (str): Set SameSite attribute for CSRF protection
    """
    
    DEBUG = False
    TESTING = False
    
    # Production-specific settings
    LOG_LEVEL = 'INFO'
    
    # Strict security in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax' 