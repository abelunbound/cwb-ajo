#!/usr/bin/env python3
"""Test Task 1 configuration system specifically."""

import os
import sys

def test_direct_env_access():
    """Test direct environment variable access."""
    print("=== Testing Direct Environment Access ===")
    required_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST']
    
    for var in required_vars:
        value = os.getenv(var)
        print(f"{var}: {value}")
    print()

def test_config_classes():
    """Test our configuration classes."""
    print("=== Testing Configuration Classes ===")
    
    try:
        # Test BaseConfig
        from config.base import BaseConfig
        print("✅ BaseConfig imported successfully")
        
        # Test validation
        BaseConfig.validate_config()
        print("✅ BaseConfig validation passed")
        
        # Test DevelopmentConfig
        from config.development import DevelopmentConfig
        dev_config = DevelopmentConfig()
        print("✅ DevelopmentConfig created successfully")
        print(f"  - DB_NAME: {dev_config.DB_NAME}")
        print(f"  - DB_HOST: {dev_config.DB_HOST}")
        
        # Test ProductionConfig
        from config.production import ProductionConfig
        prod_config = ProductionConfig()
        print("✅ ProductionConfig created successfully")
        
    except Exception as e:
        print(f"❌ Configuration classes test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_get_config_function():
    """Test the get_config function."""
    print("\n=== Testing get_config Function ===")
    
    try:
        from functions.database import get_config
        print("✅ get_config imported successfully")
        
        config = get_config()
        print("✅ get_config() executed successfully")
        print(f"  - Config type: {type(config)}")
        print(f"  - DB_NAME: {config.DB_NAME}")
        print(f"  - DB_HOST: {config.DB_HOST}")
        print(f"  - DEBUG: {config.DEBUG}")
        
    except Exception as e:
        print(f"❌ get_config test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_database_connection():
    """Test database connection."""
    print("\n=== Testing Database Connection ===")
    
    try:
        from functions.database import get_db_connection
        print("✅ get_db_connection imported successfully")
        
        connection = get_db_connection()
        if connection:
            print("✅ Database connection successful")
            connection.close()
            return True
        else:
            print("❌ Database connection returned None")
            return False
            
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Task 1 Configuration System Test ===\n")
    
    # Test each component
    test_direct_env_access()
    config_classes_ok = test_config_classes()
    get_config_ok = test_get_config_function()
    db_connection_ok = test_database_connection()
    
    print(f"\n=== Test Summary ===")
    print(f"Configuration Classes: {'✅ PASS' if config_classes_ok else '❌ FAIL'}")
    print(f"get_config Function:   {'✅ PASS' if get_config_ok else '❌ FAIL'}")
    print(f"Database Connection:   {'✅ PASS' if db_connection_ok else '❌ FAIL'}")
    
    if config_classes_ok and get_config_ok and db_connection_ok:
        print(f"\n🎉 Task 1 Configuration System: WORKING!")
    else:
        print(f"\n⚠️  Task 1 Configuration System: ISSUES DETECTED")
        
    # Test what environment we're detecting
    print(f"\n=== Environment Detection ===")
    dash_env = os.getenv('DASH_ENV')
    flask_env = os.getenv('FLASK_ENV')
    detected = dash_env or flask_env or 'development (default)'
    print(f"DASH_ENV: {dash_env}")
    print(f"FLASK_ENV: {flask_env}")
    print(f"Detected Environment: {detected}") 