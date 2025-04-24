import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "you-should-change-this")
    MYSQL_HOST = "127.0.0.1"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = ""           # or your phpMyAdmin root PW
    MYSQL_DB = "syllabot"
    MYSQL_CURSORCLASS = "DictCursor"
