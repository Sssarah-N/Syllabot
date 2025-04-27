import mysql.connector
from mysql.connector import Error

def test_aiven_connection():
    # Aiven database credentials
    host = "mysql-syllabot-syllabot.l.aivencloud.com"
    port = 25840
    user = "avnadmin"
    password = "AVNS_18iQd0hdK7JR4o1_RAo"
    database = "defaultdb"

    print("Testing direct connection to Aiven MySQL:")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"User: {user}")
    print(f"Database: {database}")
    
    try:
        # Set up connection parameters with SSL
        print("\nAttempting connection with SSL disabled...")
        
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            ssl_disabled=True
        )
        
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
        print(f"Error connecting to Aiven MySQL: {e}")
        
        # Try with a different approach if the first one fails
        try:
            print("\nTrying alternative connection method...")
            
            connection = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database
            )
            
            if connection.is_connected():
                print("Alternative connection successful!")
                connection.close()
                return True
                
        except Error as e2:
            print(f"Alternative connection also failed: {e2}")
    
    return False

if __name__ == "__main__":
    test_aiven_connection() 