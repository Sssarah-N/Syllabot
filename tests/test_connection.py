import mysql.connector
from mysql.connector import Error
import os
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

def test_connection():
    try:
        print("Attempting to connect to MySQL database...")
        print(f"Host: {Config.MYSQL_HOST}")
        print(f"Port: {Config.MYSQL_PORT}")
        print(f"User: {Config.MYSQL_USER}")
        print(f"Database: {Config.MYSQL_DB}")
        
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
            db_info = connection.get_server_info()
            print(f"Connected to MySQL Server version {db_info}")
            
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print(f"Connected to database: {record[0]}")
            
            # Try creating a test table
            try:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_connection (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    test_col VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                print("Test table created successfully")
                
                # Insert test data
                cursor.execute("""
                INSERT INTO test_connection (test_col) VALUES ('Test connection successful')
                """)
                connection.commit()
                print("Test data inserted successfully")
                
                # Query test data
                cursor.execute("SELECT * FROM test_connection")
                rows = cursor.fetchall()
                print("Test data:")
                for row in rows:
                    print(row)
            except Error as e:
                print(f"Error creating test table: {e}")
                
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

if __name__ == "__main__":
    test_connection() 