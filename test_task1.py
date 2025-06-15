#!/usr/bin/env python3
"""Test script for Task 1: Environment Configuration System"""

import os
import sys

def test_config_system():
    """Test the configuration system."""
    print("\n=== Testing Configuration System ===")
    
    try:
        from config.base import BaseConfig
        from config.development import DevelopmentConfig
        from config.production import ProductionConfig
        print("✅ Configuration classes imported successfully")
        
        # Test development config
        dev_config = DevelopmentConfig()
        print(f"✅ Development config created: DEBUG={dev_config.DEBUG}")
        
        # Test production config  
        prod_config = ProductionConfig()
        print(f"✅ Production config created: DEBUG={prod_config.DEBUG}")
        
        # Test validation
        dev_config.validate_config()
        print("✅ Configuration validation passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_variables():
    """Test environment variable loading."""
    print("\n=== Testing Environment Variables ===")
    
    try:
        from config.development import DevelopmentConfig
        config = DevelopmentConfig()
        
        print(f"DB_NAME: {config.DB_NAME}")
        print(f"DB_USER: {config.DB_USER}")
        print(f"DB_HOST: {config.DB_HOST}")
        print(f"DB_PORT: {config.DB_PORT}")
        
        if config.DB_NAME and config.DB_USER and config.DB_HOST:
            print("✅ Environment variables loaded successfully")
            return True
        else:
            print("❌ Some environment variables are missing")
            return False
            
    except Exception as e:
        print(f"❌ Environment variable test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_selection():
    """Test configuration selection based on environment."""
    print("\n=== Testing Configuration Selection ===")
    
    try:
        from functions.database import get_config
        
        # Test default (development)
        config = get_config()
        print(f"✅ Default config loaded: {type(config).__name__}")
        
        # Test with DASH_ENV
        os.environ['DASH_ENV'] = 'production'
        config = get_config()
        print(f"✅ Production config loaded: {type(config).__name__}")
        
        # Reset environment
        if 'DASH_ENV' in os.environ:
            del os.environ['DASH_ENV']
            
        return True
        
    except Exception as e:
        print(f"❌ Configuration selection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

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

def main():
    """Run all tests."""
    print("Starting Task 1 Tests...")
    
    tests = [
        test_config_system,
        test_environment_variables,
        test_config_selection,
        test_database_connection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Task 1 is complete.")
        return True
    else:
        print("❌ Some tests failed. Please check the configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 