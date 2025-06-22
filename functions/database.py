import psycopg2
import pandas as pd
import numpy as np
import os
from pathlib import Path
from config.development import DevelopmentConfig
from config.production import ProductionConfig
np.bool = np.bool_ # https://stackoverflow.com/questions/74893742/how-to-solve-attributeerror-module-numpy-has-no-attribute-bool

# Get configuration based on environment
def get_config():
    """Get configuration based on DASH_ENV or FLASK_ENV environment variable.
    
    Determines the appropriate configuration class to use based on environment
    variables. Checks DASH_ENV first, then FLASK_ENV, defaulting to development.
    
    Returns:
        BaseConfig: Configuration instance (DevelopmentConfig or ProductionConfig)
        
    Raises:
        ValueError: If required environment variables are missing
    """
    # Try DASH_ENV first, then FLASK_ENV, then default to development
    env = os.getenv('DASH_ENV') or os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        config = ProductionConfig()
    else:
        config = DevelopmentConfig()
    
            # Validate configuration
        config.validate_config()
    return config

# Insert the data into the SQL database - modified to use execute many

def get_column_name_and_datatype_dictionary(df):
    """
    Convert DataFrame column names and types to SQL-compatible dictionary format.
    
    Parameters:
    df (DataFrame): Pandas DataFrame to extract column information from
    
    Returns:
    dict: Dictionary mapping column names to SQL data types
    """
    # Get DataFrame dtypes as dictionary
    dtype_dict = df.dtypes.to_dict()
    
    # Map pandas dtypes to SQL types
    sql_type_mapping = {
        'int64': 'INTEGER',
        'int32': 'INTEGER',
        'float64': 'FLOAT',
        'float32': 'FLOAT',
        'bool': 'BOOLEAN',
        'datetime64[ns]': 'TIMESTAMP',
        'object': 'VARCHAR(255)',  # Default for strings/objects
        'category': 'VARCHAR(255)',
        'timedelta64[ns]': 'INTERVAL'
    }
    
    # Create column definitions dictionary
    column_definitions = {}
    for column, dtype in dtype_dict.items():
        # Convert dtype to string and extract the type name
        dtype_str = str(dtype)
        # Map pandas dtype to SQL type
        if dtype_str in sql_type_mapping:
            sql_type = sql_type_mapping[dtype_str]
        else:
            sql_type = 'VARCHAR(255)'  # Default fallback
        
        column_definitions[column] = sql_type
    
    return column_definitions



# Helper function to convert boolean values to Python bool type (this resolve the "can't adapt type 'numpy.bool_'" error.)
def convert_value(value, col, boolean_columns):
    if isinstance(value, np.bool_):
        return bool(value)
    elif col in boolean_columns:
        return bool(value)
    return value


def prepare_sql_queries_and_values(column_definitions, table_name, data):
    """
    Prepare SQL queries and values for creating a table and upserting data based on a composite key.
    
    Parameters:
    column_definitions (dict): Dictionary mapping column names to SQL data types
    table_name (str): Name of the table to create/insert into
    data (DataFrame): Pandas DataFrame containing the data to insert
    
    Returns:
    tuple: (table_query, insert_query, values_list)
    """
    # Extract just the column names for other operations
    columns = list(column_definitions.keys())
    
    # Define the composite unique columns for upsert operations
    primary_key_columns = ["applicant_id", "sn"]
    
    # Boolean columns for conversion
    boolean_columns = [col for col, type_def in column_definitions.items() if type_def == 'BOOLEAN']
    
    # Create table query with unique constraint on the composite key
    table_columns_definition = ",\n            ".join(f"{col} {data_type}" for col, data_type in column_definitions.items())
    constraints = f",\n            CONSTRAINT {table_name}_pk PRIMARY KEY ({', '.join(primary_key_columns)})"
    
    table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
            {table_columns_definition}{constraints}
    ) 
    """
    
    # Create upsert query (INSERT ... ON CONFLICT)
    columns_str = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    
    # Create the update clause for all columns except the primary key columns
    non_key_columns = [col for col in columns if col not in primary_key_columns]
    update_clause = ", ".join([f"{col} = EXCLUDED.{col}" for col in non_key_columns])
    
    insert_query = f"""
    INSERT INTO {table_name} ({columns_str}) 
    VALUES ({placeholders})
    ON CONFLICT ({', '.join(primary_key_columns)}) 
    DO UPDATE SET {update_clause}
    """
    
    # Create values list with proper type conversion
    # values_list = [
    #     tuple(bool(row[col]) if col in boolean_columns else row[col] for col in columns)
    #     for index, row in data.iterrows()
    # ]
    
    values_list = [
    tuple(convert_value(row[col], col, boolean_columns) for col in columns)
    for index, row in data.iterrows()
]
    return table_query, insert_query, values_list



def get_db_connection():
    """Create a database connection using configuration system.
    
    Establishes a PostgreSQL database connection using credentials
    from the configuration system. Handles connection errors gracefully.
    
    Returns:
        psycopg2.connection: Database connection object or None if connection fails
        
    Raises:
        psycopg2.Error: Database connection errors are caught and logged
        ValueError: Configuration validation errors are caught and logged
    """
    try:
        config = get_config()
        
        connection = psycopg2.connect(
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=config.DB_PORT
        )
        print(f"\nConnected to database...'{config.DB_NAME}'")
        return connection 
    
    except psycopg2.Error as error:
        print(f"Error connecting to the database: {error}")
        return None
    except ValueError as error:
        print(f"Configuration error: {error}")
        return None

def get_ajo_db_connection():
    """Create a database connection to the Ajo platform database.
    
    Establishes a PostgreSQL database connection to the ajo-platform-db
    using credentials from the configuration system. This is specifically
    for Ajo-related functionality (groups, members, contributions, etc.).
    
    Returns:
        psycopg2.connection: Database connection object or None if connection fails
        
    Raises:
        psycopg2.Error: Database connection errors are caught and logged
        ValueError: Configuration validation errors are caught and logged
    """
    try:
        config = get_config()
        
        connection = psycopg2.connect(
            dbname=config.AJO_DB_NAME,
            user=config.AJO_DB_USER,
            password=config.AJO_DB_PASSWORD,
            host=config.AJO_DB_HOST,
            port=config.AJO_DB_PORT
        )
        print(f"\nConnected to Ajo database...'{config.AJO_DB_NAME}'")
        return connection 
    
    except psycopg2.Error as error:
        print(f"Error connecting to the Ajo database: {error}")
        return None
    except ValueError as error:
        print(f"Configuration error: {error}")
        return None

def insert_data_into_sql_data_base(table_query, insert_query, values_list):
    """
    Insert data into the database using prepared SQL components.
    
    Parameters:
    table_query (str): SQL query to create the table
    insert_query (str): SQL query to insert data
    values_list (list): List of value tuples to insert
    
    Returns:
    None
    """
    try:
        # Create connection to the SQL database
        connection = get_db_connection()

        # Defensive programming - check if connection was successful
        if not connection:
            return
        
        # Create a cursor 
        cursor = connection.cursor()

        # Extract table name from the CREATE TABLE query

        # This assumes your table_query follows the format "CREATE TABLE IF NOT EXISTS table_name (...)"
        table_name = table_query.split('CREATE TABLE IF NOT EXISTS ')[1].split('(')[0].strip()
        
        # # Drop the existing table - added once when I needed to have a table with a different column structyre but same name
        # drop_query = f"DROP TABLE IF EXISTS {table_name}"
        # cursor.execute(drop_query)
        # print(f"Dropped table {table_name} if it existed")
      
        # Create a table
        cursor.execute(table_query)
        
        # Execute batch insert
        print(f"Inserting {len(values_list)} rows in a batch...into table '{table_name}'")
        
        cursor.executemany(insert_query, values_list)
        
        # Commit the data into the connection
        connection.commit()
        
        # Success note/ Inform user
        print("Your data has been inserted successfully into the SQL database...")
        
    except psycopg2.Error as error:
        print(f" an error has occurred : {error}")
        
    finally:
        if "connection" in locals() and connection is not None:
            cursor.close()
            connection.close()
            print("Your connection is closed\n")




def retrieve_data_from_sql(table_name):
    """
    Retrieve data from a specified SQL table and return it as a pandas DataFrame.
    
    This function establishes a connection to the database, executes a SELECT query
    to fetch records from the specified table, and converts the results into a
    pandas DataFrame with appropriate column names.
    
    Parameters:
    ----------
    table_name : str
        The name of the SQL table to retrieve data from
        
    Returns:
    -------
    pandas.DataFrame
        A DataFrame containing all records from the specified table,
        with columns named according to the table schema.
        Returns None if connection fails or an error occurs.
    
    Raises:
    ------
    The function handles exceptions internally and prints error messages,
    but does not raise exceptions to the caller.
    """
    try:
        # Create connection to the SQL database
        connection = get_db_connection()

        # Defensive programming - check if connection was successful
        if not connection:
            return
        
        # Create a cursor
        cursor = connection.cursor()
        
        # Retrieve Data from the table
        table_query = f"SELECT * FROM {table_name}"
        cursor.execute(table_query)
        result = cursor.fetchall()
        
        # Convert the data from the SQL database to a dataframe
        column_name = [header[0] for header in cursor.description] # what other items are held in the cursor.description 
        df = pd.DataFrame(result, columns= column_name) 

        # Success note/ Inform user
        
        print("Your data has retrieved successfully from the SQL database...")
        print(f"Data frame with length: {len(df)} retrieved from {table_name}...")
        
    except psycopg2.Error as error:
        print(f"You have encountered an error: {error}")
    finally:
        if "connection" in locals() and connection is not None:
            cursor.close()
            connection.close()
            print("Your connection is closed")
    return df



def add_metadata_columns(df, applicant_id="123456789"):
    """
    Add metadata columns to a DataFrame with user ID, current date, and transaction time.
    
    Parameters:
    ----------
    df : pandas.DataFrame
        The DataFrame to add columns to
    applicant_id : str, optional
        The user ID to add to all rows (default: "1234")
        
    Returns:
    -------
    pandas.DataFrame
        The DataFrame with the additional columns
    """
    # Create a copy to avoid modifying the original DataFrame
    result_df = df.copy()
    
    # Add metadata columns with proper datetime objects
    result_df['applicant_id'] = applicant_id
    result_df['date_added'] = pd.Timestamp.now().date()
    result_df['transaction_time'] = pd.Timestamp.now()

    # Add sequence number starting from 1
    result_df['sn'] = range(1, len(result_df) + 1)
    
    return result_df

# ==============================
# TASK 29: GROUP INVITATION SYSTEM
# ==============================

def create_group_invitation(group_id, inviter_user_id, invitee_email):
    """Create a new group invitation.
    
    Args:
        group_id (int): ID of the group to invite to
        inviter_user_id (int): ID of the user sending the invitation
        invitee_email (str): Email address of the person being invited
        
    Returns:
        dict: Invitation details including invitation_code, or None if error
    """
    try:
        connection = get_ajo_db_connection()
        if not connection:
            return None
            
        cursor = connection.cursor()
        
        # First, expire old invitations automatically
        cursor.execute("SELECT expire_old_invitations()")
        
        # Generate unique invitation code
        cursor.execute("SELECT generate_invitation_code()")
        invitation_code = cursor.fetchone()[0]
        
        # Set expiration to 7 days from now
        insert_query = """
        INSERT INTO ajo_group_invitations 
        (group_id, inviter_user_id, invitee_email, invitation_code, expires_at) 
        VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP + INTERVAL '7 days')
        RETURNING id, invitation_code, expires_at
        """
        
        cursor.execute(insert_query, (group_id, inviter_user_id, invitee_email, invitation_code))
        result = cursor.fetchone()
        
        connection.commit()
        
        print(f"Created invitation: {invitation_code} for {invitee_email}")
        
        return {
            'id': result[0],
            'invitation_code': result[1],
            'expires_at': result[2],
            'invitee_email': invitee_email
        }
        
    except psycopg2.Error as error:
        print(f"Error creating invitation: {error}")
        return None
    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()

def get_invitation_by_code(invitation_code):
    """Retrieve invitation details by invitation code.
    
    Args:
        invitation_code (str): The unique invitation code
        
    Returns:
        dict: Invitation details with group info, or None if not found
    """
    try:
        connection = get_ajo_db_connection()
        if not connection:
            return None
            
        cursor = connection.cursor()
        
        # First, expire old invitations
        cursor.execute("SELECT expire_old_invitations()")
        
        query = """
        SELECT 
            i.id, i.group_id, i.inviter_user_id, i.invitee_email,
            i.invitation_code, i.status, i.expires_at, i.created_at,
            g.name as group_name, g.description as group_description,
            g.contribution_amount, g.frequency, g.duration_months,
            g.max_members,
            (SELECT COUNT(*) FROM group_members WHERE group_id = g.id AND status = 'active') as current_members
        FROM ajo_group_invitations i
        JOIN ajo_groups g ON i.group_id = g.id
        WHERE i.invitation_code = %s
        """
        
        cursor.execute(query, (invitation_code,))
        result = cursor.fetchone()
        
        if not result:
            return None
            
        return {
            'id': result[0],
            'group_id': result[1],
            'inviter_user_id': result[2],
            'invitee_email': result[3],
            'invitation_code': result[4],
            'status': result[5],
            'expires_at': result[6],
            'created_at': result[7],
            'group_name': result[8],
            'group_description': result[9],
            'contribution_amount': result[10],
            'frequency': result[11],
            'duration_months': result[12],
            'max_members': result[13],
            'current_members': result[14]
        }
        
    except psycopg2.Error as error:
        print(f"Error retrieving invitation: {error}")
        return None
    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()

def update_invitation_status(invitation_code, status):
    """Update the status of an invitation.
    
    Args:
        invitation_code (str): The unique invitation code
        status (str): New status ('accepted', 'declined', 'expired')
        
    Returns:
        bool: True if update successful, False otherwise
    """
    try:
        connection = get_ajo_db_connection()
        if not connection:
            return False
            
        cursor = connection.cursor()
        
        update_query = """
        UPDATE ajo_group_invitations 
        SET status = %s 
        WHERE invitation_code = %s AND status = 'pending'
        """
        
        cursor.execute(update_query, (status, invitation_code))
        rows_affected = cursor.rowcount
        
        connection.commit()
        
        if rows_affected > 0:
            print(f"Updated invitation {invitation_code} status to {status}")
            return True
        else:
            print(f"No pending invitation found with code {invitation_code}")
            return False
        
    except psycopg2.Error as error:
        print(f"Error updating invitation status: {error}")
        return False
    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()

def get_group_invitations(group_id):
    """Get all invitations for a specific group.
    
    Args:
        group_id (int): ID of the group
        
    Returns:
        list: List of invitation dictionaries
    """
    try:
        connection = get_ajo_db_connection()
        if not connection:
            return []
            
        cursor = connection.cursor()
        
        # First, expire old invitations
        cursor.execute("SELECT expire_old_invitations()")
        
        query = """
        SELECT 
            id, invitee_email, invitation_code, status, 
            expires_at, created_at, accepted_at, declined_at
        FROM ajo_group_invitations 
        WHERE group_id = %s 
        ORDER BY created_at DESC
        """
        
        cursor.execute(query, (group_id,))
        results = cursor.fetchall()
        
        invitations = []
        for row in results:
            invitations.append({
                'id': row[0],
                'invitee_email': row[1],
                'invitation_code': row[2],
                'status': row[3],
                'expires_at': row[4],
                'created_at': row[5],
                'accepted_at': row[6],
                'declined_at': row[7]
            })
            
        return invitations
        
    except psycopg2.Error as error:
        print(f"Error retrieving group invitations: {error}")
        return []
    finally:
        if 'connection' in locals() and connection:
            cursor.close()
            connection.close()

def add_user_to_group(user_id, group_id):
    """Add a user to a group (for invitation acceptance).
    
    Args:
        user_id (int): ID of the user to add
        group_id (int): ID of the group to add user to
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Use the existing group membership service
        from functions.group_membership_service import add_member_to_group
        
        result = add_member_to_group(group_id, user_id, role='member')
        
        if result['success']:
            print(f"Added user {user_id} to group {group_id} at position {result['payment_position']}")
            return True
        else:
            print(f"Failed to add user to group: {result['error']}")
            return False
        
    except Exception as error:
        print(f"Error adding user to group: {error}")
        return False