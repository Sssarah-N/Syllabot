import mysql.connector
from mysql.connector import Error
import os
from config import Config

def test_connection():
    try:
        print("Testing database connection using environment variables:")
        print(f"Host: {Config.MYSQL_HOST}")
        print(f"Port: {Config.MYSQL_PORT}")
        print(f"User: {Config.MYSQL_USER}")
        print(f"Database: {Config.MYSQL_DB}")
        
        # Determine if we're using Aiven (by checking host name)
        is_aiven = "aivencloud.com" in Config.MYSQL_HOST
        
        # Set up connection parameters
        conn_params = {
            'host': Config.MYSQL_HOST,
            'user': Config.MYSQL_USER,
            'password': Config.MYSQL_PASSWORD,
            'database': Config.MYSQL_DB,
            'port': Config.MYSQL_PORT
        }
        
        # Add SSL configuration for Aiven
        if is_aiven:
            print("Using Aiven configuration with SSL settings")
            conn_params.update({
                'ssl_disabled': False,
                'ssl_verify_cert': False  # Disable certificate verification for easier connection
            })
        else:
            print("Using standard local database configuration")
        
        # Try different connection approaches
        try:
            print("\nAttempting connection...")
            connection = mysql.connector.connect(**conn_params)
            
            if connection.is_connected():
                db_info = connection.get_server_info()
                print(f"Connected to MySQL Server version {db_info}")
                
                cursor = connection.cursor()
                cursor.execute("SELECT DATABASE();")
                record = cursor.fetchone()
                print(f"Connected to database: {record[0]}")
                
                # Try simple query
                cursor.execute("SHOW TABLES;")
                tables = cursor.fetchall()
                print("\nTables in the database:")
                if tables:
                    for table in tables:
                        print(f"- {table[0]}")
                else:
                    print("No tables found in the database")
                
                connection.close()
                print("MySQL connection is closed")
                return True
                
        except Error as e:
            print(f"Error during connection attempt 1: {e}")
        
    except Error as e:
        print(f"General error: {e}")
        
    return False

if __name__ == "__main__":
    test_connection() 