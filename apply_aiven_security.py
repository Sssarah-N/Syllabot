#!/usr/bin/env python3
"""
Aiven MySQL Security Configuration Script

This script applies the security measures defined in aiven_db_security.sql 
to the Aiven MySQL database for Syllabot.

Usage:
    python apply_aiven_security.py
"""

import mysql.connector
from mysql.connector import Error
import sys
import os
from config import Config
import re

def apply_security_measures():
    """Connect to Aiven MySQL and execute security SQL statements"""
    
    # Path to the security SQL file
    sql_file_path = 'aiven_db_security.sql'
    
    # Read SQL commands from file
    try:
        with open(sql_file_path, 'r') as file:
            sql_content = file.read()
        print(f"Successfully read SQL file: {sql_file_path}")
        
        # Print the credentials that will be used
        print(f"Using connection parameters:")
        print(f"  Host: {Config.MYSQL_HOST}")
        print(f"  User: {Config.MYSQL_USER}")
        print(f"  Database: {Config.MYSQL_DB}")
        print(f"  Port: {Config.MYSQL_PORT}")
        print(f"  SSL Disabled: False")
    except Exception as e:
        print(f"Error reading SQL file: {e}")
        return False
    
    # Connect to the Aiven MySQL database as admin
    try:
        print("Connecting to Aiven MySQL database as admin user...")
        conn_params = {
            'host': Config.MYSQL_HOST,
            'user': Config.MYSQL_USER,
            'password': Config.MYSQL_PASSWORD,
            'database': Config.MYSQL_DB,
            'port': Config.MYSQL_PORT,
            'ssl_disabled': False
        }
        
        connection = mysql.connector.connect(**conn_params)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"Connected to MySQL Server version {db_info}")
            
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print(f"Connected to database: {record[0]}")
            
            # Split SQL statements by semicolon and execute
            sql_commands = sql_content.split(';')
            
            # Execute each SQL command
            for command in sql_commands:
                # Skip empty commands or comments
                command = command.strip()
                if command and not command.startswith('--'):
                    try:
                        cursor.execute(command)
                        print(f"Successfully executed: {command[:50]}..." if len(command) > 50 else f"Successfully executed: {command}")
                    except Error as e:
                        print(f"Error executing command: {e}")
                        print(f"Command was: {command}")
            
            # Commit changes
            connection.commit()
            print("All security SQL commands executed successfully.")
            return True
            
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed")

def verify_users():
    """Verify that users were created correctly"""
    try:
        # Connect to DB with admin privileges
        conn_params = {
            'host': Config.MYSQL_HOST,
            'user': Config.MYSQL_USER,
            'password': Config.MYSQL_PASSWORD,
            'database': Config.MYSQL_DB,
            'port': Config.MYSQL_PORT,
            'ssl_disabled': False
        }
        
        print("\nVerifying users with connection parameters:")
        print(f"  Host: {Config.MYSQL_HOST}")
        print(f"  User: {Config.MYSQL_USER}")
        print(f"  Database: {Config.MYSQL_DB}")
        print(f"  Port: {Config.MYSQL_PORT}")
        
        connection = mysql.connector.connect(**conn_params)
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Query to list users
            cursor.execute("SELECT user, host FROM mysql.user WHERE user LIKE 'syllabot%' OR user = 'student_role';")
            users = cursor.fetchall()
            
            print("\nVerifying created users:")
            if users:
                for user in users:
                    print(f"- User: {user[0]}, Host: {user[1]}")
                    
                    # Check grants for this user
                    try:
                        cursor.execute(f"SHOW GRANTS FOR '{user[0]}'@'{user[1]}';")
                        grants = cursor.fetchall()
                        print(f"  Privileges for {user[0]}:")
                        for grant in grants:
                            print(f"    {grant[0]}")
                    except Error as e:
                        print(f"  Error checking privileges: {e}")
            else:
                print("No Syllabot users found. Security setup may have failed.")
                
            return True
    except Error as e:
        print(f"Error verifying users: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def update_admin_password():
    """Update the admin password to match the security file"""
    try:
        # Read the security SQL file to extract passwords
        with open('aiven_db_security.sql', 'r') as file:
            sql_content = file.read()
        
        # Look for admin (dev) password in SQL file
        dev_password_match = re.search(r"CREATE USER IF NOT EXISTS 'syllabot_dev'@'%' IDENTIFIED BY '(.*?)';", sql_content)
        
        if dev_password_match:
            admin_password = dev_password_match.group(1)
            print(f"\nAdmin password found in security file: {admin_password}")
            
            # Path to config file
            config_path = 'config.py'
            
            # Read current config
            with open(config_path, 'r') as file:
                config_content = file.read()
            
            # Update admin password in config file
            updated_config = re.sub(
                r'ADMIN_PASSWORD = ".*?"', 
                f'ADMIN_PASSWORD = "{admin_password}"', 
                config_content
            )
            
            # Write updated config
            with open(config_path, 'w') as file:
                file.write(updated_config)
            
            print(f"Config file updated with new admin password.")
            return True
        else:
            print("Could not find admin password in security file.")
            return False
            
    except Exception as e:
        print(f"Error updating admin password: {e}")
        return False

if __name__ == "__main__":
    print("Applying Aiven MySQL security measures...")
    if apply_security_measures():
        print("\nSecurity measures applied successfully.")
        verify_users()
        update_admin_password()
        print("\nDatabase security setup complete. You can now use the application with proper security roles.")
    else:
        print("\nFailed to apply security measures. Please check the error messages above.")
        sys.exit(1) 