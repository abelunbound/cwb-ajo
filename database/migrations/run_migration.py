import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration(sql_file_path=None):
    """Run any SQL migration file on the Ajo database"""
    
    # Handle command line argument or prompt for file path
    if not sql_file_path:
        if len(sys.argv) > 1:
            sql_file_path = sys.argv[1]
        else:
            sql_file_path = input("Enter SQL migration file path: ")
    
    try:
        # Get AJO database connection parameters from environment variables
        db_params = {
            'dbname': os.getenv('AJO_DB_NAME'),
            'user': os.getenv('AJO_DB_USER'),
            'password': os.getenv('AJO_DB_PASSWORD'),
            'host': os.getenv('AJO_DB_HOST'),
            'port': os.getenv('AJO_DB_PORT', '5432')
        }
        
        # Validate that required environment variables are set
        missing_vars = [key for key, value in db_params.items() if not value and key != 'port']
        if missing_vars:
            raise ValueError(f"Missing required AJO database environment variables: {missing_vars}")
        
        print(f"Connecting to AJO database: {db_params['dbname']} at {db_params['host']}")
        
        # Connect to the AJO database
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        
        # Read and execute the migration file
        print(f"Running migration: {sql_file_path}")
        with open(sql_file_path, 'r') as f:
            migration_sql = f.read()
            cur.execute(migration_sql)
        
        # Commit the changes
        conn.commit()
        print(f"Migration {sql_file_path} completed successfully!")
        
    except FileNotFoundError:
        print(f"Error: Migration file '{sql_file_path}' not found")
    except ValueError as e:
        print(f"Configuration error: {e}")
    except psycopg2.Error as e:
        print(f"Database error running migration: {e}")
        if 'conn' in locals():
            conn.rollback()
    except Exception as e:
        print(f"Unexpected error running migration: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_migration() 