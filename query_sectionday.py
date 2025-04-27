import mysql.connector
from mysql.connector import Error
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import Config
from aiven_db_connect import connect_to_aiven, close_connection

def query_sectionday_table():
    """
    Query and display the contents of the sectionday table
    """
    connection, cursor = connect_to_aiven()
    
    if connection and cursor:
        try:
            # SQL query to select all data from the sectionday table
            sql_query = """
            SELECT * FROM sectionday;
            """
            
            print("\nExecuting query: " + sql_query.strip())
            
            # Execute the query
            cursor.execute(sql_query)
            
            # Fetch all rows
            rows = cursor.fetchall()
            
            # Get column names
            field_names = [i[0] for i in cursor.description]
            
            # Display column headers
            print("\nSectionday Table:")
            print("-" * 30)
            print(" | ".join(field_names))
            print("-" * 30)
            
            # Display data
            if rows:
                for row in rows:
                    print(" | ".join(str(value) for value in row))
            else:
                print("No data found in the sectionday table.")
                
        except Error as e:
            print(f"Error executing SQL query: {e}")
            
        # Keep connection open as requested
        print("\nConnection remains open. To close it, use close_connection(connection, cursor)")
        
        # Make connection and cursor available globally
        return connection, cursor
    else:
        print("Failed to connect to the database.")
        return None, None

if __name__ == "__main__":
    query_sectionday_table() 