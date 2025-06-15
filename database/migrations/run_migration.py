import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Run the SQL migration file to create financial health tables"""
    try:
        # Get database connection parameters from environment variables
        db_params = {
            'dbname': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST')
        }
        
        # Connect to the database
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()
        
        # Read and execute the migration file
        with open('database/migrations/003_create_finhealth_tables.sql', 'r') as f:
            migration_sql = f.read()
            cur.execute(migration_sql)
        
        # Commit the changes
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error running migration: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    run_migration() 