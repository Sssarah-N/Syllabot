from config import Config

def print_active_config():
    print("Active Configuration Settings:")
    print(f"Environment Type: {Config.ENV_TYPE}")
    print(f"SSL Enabled: {Config.SSL_ENABLED}")
    print(f"Host: {Config.MYSQL_HOST}")
    print(f"Port: {Config.MYSQL_PORT}")
    print(f"User: {Config.MYSQL_USER}")
    print(f"Database: {Config.MYSQL_DB}")
    print(f"MySQL Cursor Class: {Config.MYSQL_CURSORCLASS}")

if __name__ == "__main__":
    print_active_config() 