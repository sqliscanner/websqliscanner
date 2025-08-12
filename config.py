import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret123')
    MYSQL_HOST = os.getenv('MYSQLHOST', 'localhost')         
    MYSQL_USER = os.getenv('MYSQLUSER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQLPASSWORD', '')
    MYSQL_DB = os.getenv('MYSQLDATABASE', 'sqli_scanner')
