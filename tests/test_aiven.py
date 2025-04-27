import mysql.connector
from mysql.connector import Error

def test_aiven_connection():
    try:
        print("Attempting to connect to Aiven MySQL database...")
        # Direct credentials instead of environment variables
        host = "mysql-syllabot-syllabot.aivencloud.com"
        port = 25840
        user = "avnadmin"
        password = "AVNS_18iQd0hdK7JR4o1_RAo"
        database = "defaultdb"
        
        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"User: {user}")
        print(f"Database: {database}")
        
        # Try connecting with SSL options
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            ssl_disabled=False,
            ssl_verify_cert=False  # Disable certificate verification for testing
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
                INSERT INTO test_connection (test_col) VALUES ('Aiven connection successful')
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
    test_aiven_connection() 