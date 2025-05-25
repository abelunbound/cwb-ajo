import psycopg2
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os
from pathlib import Path
np.bool = np.bool_ # https://stackoverflow.com/questions/74893742/how-to-solve-attributeerror-module-numpy-has-no-attribute-bool

# Load environment variables from the functions directory
env_path = Path(__file__).parent / 'cwb-db.env'
load_dotenv(env_path)

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
    """
    Creates a database connection using environment variables
    
    TODO: Security Improvement Needed
    - Remove hardcoded fallback credentials before deploying to production
    - Add proper error handling for missing environment variables
    - See TODO.md for complete list of pending security improvements
    """
    try:
        connection = psycopg2.connect(
            dbname=os.getenv('DB_NAME', 'cwb-database').strip("'"),
            user=os.getenv('DB_USER', 'abelakeni').strip("'"),
            password=os.getenv('DB_PASSWORD', 'unbound365').strip("'"),
            host=os.getenv('DB_HOST', '35.192.88.249').strip("'"),
            port=os.getenv('DB_PORT', '5432').strip("'")   
        )
        print(f"\nConnected to database...'{os.getenv('DB_NAME', 'cwb-database')}'")
        return connection 
    
    except psycopg2.Error as error:
        print(f"Error connecting to the database: {error}")
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