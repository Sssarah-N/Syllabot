import mysql.connector
from mysql.connector import Error
import os
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import Config

def connect_to_aiven():
    """
    Connect to the Aiven MySQL database using config settings
    """
    try:
        print("Connecting to Aiven MySQL database...")
        print(f"Host: {Config.MYSQL_HOST}")
        print(f"Port: {Config.MYSQL_PORT}")
        print(f"User: {Config.MYSQL_USER}")
        print(f"Database: {Config.MYSQL_DB}")
        
        # Set up connection parameters
        conn_params = {
            'host': Config.MYSQL_HOST,
            'user': Config.MYSQL_USER,
            'password': Config.MYSQL_PASSWORD,
            'database': Config.MYSQL_DB,
            'port': Config.MYSQL_PORT,
            'ssl_disabled': False,
            'ssl_verify_cert': False  # Disable certificate verification for easier connection
        }
        
        # Attempt connection
        connection = mysql.connector.connect(**conn_params)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Connected to MySQL Server version {db_info}")
            
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print(f"Connected to database: {record[0]}")
            
            # Show tables in the database
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print("\nTables in the database:")
            if tables:
                for table in tables:
                    print(f"- {table[0]}")
                    
                    # Show table structure
                    cursor.execute(f"DESCRIBE {table[0]};")
                    columns = cursor.fetchall()
                    print(f"  Columns in {table[0]}:")
                    for column in columns:
                        print(f"    - {column[0]}: {column[1]}")
                    print()
            else:
                print("No tables found in the database")
                
            return connection, cursor
        else:
            print("Failed to connect to the database")
            return None, None
            
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None, None

def close_connection(connection, cursor):
    """
    Close the database connection and cursor
    """
    if cursor:
        cursor.close()
    if connection and connection.is_connected():
        connection.close()
        print("MySQL connection is closed")

def update_sectionday_table():
    """
    Update the sectionday table with the provided values
    """
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            port=Config.MYSQL_PORT,
            ssl_disabled=False,
            ssl_verify_cert=False
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # First, delete existing data
            cursor.execute("DELETE FROM sectionday")
            print(f"Deleted {cursor.rowcount} rows from sectionday table")
            
            # Insert new values
            insert_data = [
                ('Mon', 2808),
                ('Tue', 3295),
                ('Fri', 7973),
                ('Mon', 8126),
                ('Mon', 8148),
                ('Mon', 8160),
                ('Mon', 8170),
                ('Tue', 8182),
                ('Mon', 8203),
                ('Mon', 8643),
                ('Wed', 8644),
                ('Mon', 10236),
                ('Mon', 10282),
                ('Mon', 10428),
                ('Mon', 10429),
                ('Tue', 10521),
                ('Mon', 10522),
                ('Tue', 10530),
                ('Tue', 12739),
                ('Wed', 14168),
                ('Mon', 14170),
                ('Tue', 14180),
                ('Tue', 15009),
                ('Fri', 15011),
                ('Mon', 15057),
                ('Tue', 15114),
                ('Wed', 19206),
                ('Mon', 20164),
                ('Mon', 20985),
                ('Tue', 20986),
                ('Fri', 21273),
                ('Thu', 21631),
                ('Thu', 22781),
                ('Fri', 22854),
                ('Thu', 22855),
                ('Wed', 23148)
            ]
            
            # Prepare SQL query
            insert_query = "INSERT INTO sectionday (day, sectionID) VALUES (%s, %s)"
            
            # Execute the insert
            cursor.executemany(insert_query, insert_data)
            connection.commit()
            
            print(f"Successfully inserted {cursor.rowcount} rows into sectionday table")
            
            # Verify the data was inserted by querying the table
            cursor.execute("SELECT COUNT(*) FROM sectionday")
            count = cursor.fetchone()[0]
            
            print(f"\nVerification: sectionday table now has {count} rows")
            
    except Error as e:
        print(f"Error updating database: {e}")
        if 'connection' in locals() and connection.is_connected():
            connection.rollback()
            
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("Database connection closed")

def execute_sql_file(file_path):
    """Execute SQL commands from a file to the MySQL database."""
    
    # Database connection parameters - adjust these to your open connection
    DB_HOST = "localhost"  # or your current host
    DB_PORT = "3306"
    DB_NAME = "defaultdb"  # your current database
    DB_USER = "root"       # your current user
    DB_PASSWORD = ""       # your current password
    
    print(f"Connecting to MySQL database: {DB_HOST}")
    
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            print("Successfully connected to MySQL database.")
            
            # Read the SQL file
            with open(file_path, 'r') as file:
                sql_content = file.read()
            
            # Split SQL statements by semicolon
            sql_commands = sql_content.split(';')
            
            # Execute each SQL command
            for command in sql_commands:
                # Skip empty commands or comments
                if command.strip() and not command.strip().startswith('--'):
                    try:
                        cursor.execute(command)
                        print(f"Successfully executed: {command[:50]}...")
                        
                        # If the command is a SELECT statement, fetch and display results
                        if command.strip().upper().startswith('SELECT'):
                            results = cursor.fetchall()
                            print("Results:")
                            for row in results:
                                print(row)
                    except mysql.connector.Error as error:
                        print(f"Error executing command: {error}")
            
            # Commit changes
            connection.commit()
            print("All SQL commands have been executed successfully.")
            
    except mysql.connector.Error as error:
        print(f"Failed to connect to MySQL database: {error}")
    
    finally:
        # Close the connection
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    # Connect to Aiven database
    connection, cursor = connect_to_aiven()
    
    # Keep connection open for interactive use
    print("\nConnection is open and ready for interactive use.")
    print("When finished, remember to run: close_connection(connection, cursor)")
    
    # Make connection and cursor available globally
    global_connection = connection
    global_cursor = cursor

    # Execute the DELETE statement
    cursor.execute("DELETE FROM sectionday")
    print(f"Deleted {cursor.rowcount} rows")

    # Execute the INSERT statements (I'll use executemany for efficiency)
    insert_data = [
        ('Mon', 2808),
        ('Tue', 3295),
        ('Fri', 7973),
        # ... add all other rows here
        ('Thu', 22855),
        ('Wed', 23148)
    ]

    cursor.executemany("INSERT INTO sectionday (day, sectionID) VALUES (%s, %s)", insert_data)
    connection.commit()
    print(f"Inserted {cursor.rowcount} rows")

    # Update sectionday table
    update_sectionday_table()

    # Check if the SQL file exists
    SQL_FILE_PATH = "check_security.sql"
    if not os.path.exists(SQL_FILE_PATH):
        print(f"Error: SQL file {SQL_FILE_PATH} does not exist.")
    else:
        execute_sql_file(SQL_FILE_PATH)
        print("Security check complete.")