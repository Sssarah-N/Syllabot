import os

class Config:
    # Common settings
    SECRET_KEY = os.environ.get("SECRET_KEY", "you-should-change-this")
    MYSQL_CURSORCLASS = "DictCursor"
    
    # Get environment type (local or aiven)
    # Change this to "aiven" to use Aiven MySQL
    ENV_TYPE = "aiven" 
    
    # Configuration based on environment type
    if ENV_TYPE == "aiven":
        # Aiven MySQL configuration
        MYSQL_HOST = "mysql-syllabot-syllabot.l.aivencloud.com"
        MYSQL_PORT = 25840
        MYSQL_USER = "avnadmin"
        MYSQL_PASSWORD = "AVNS_18iQd0hdK7JR4o1_RAo"
        MYSQL_DB = "defaultdb"
        SSL_ENABLED = True
    else:
        # Local MySQL configuration
        MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
        MYSQL_USER = os.environ.get("MYSQL_USER", "root")
        MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
        MYSQL_DB = os.environ.get("MYSQL_DB", "syllabot")
        MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
        SSL_ENABLED = False

    # User-specific credentials for role-based database access
    # These would be the users created in the aiven_db_security.sql script
    STUDENT_USER = "student_role"
    STUDENT_PASSWORD = "student_password"
    
    ADMIN_USER = "syllabot_dev"  # Admin uses the developer role with full access
    ADMIN_PASSWORD = "dev_password"
    
    # For read-only operations
    READONLY_USER = "syllabot_readonly"
    READONLY_PASSWORD = "readonly_password"
