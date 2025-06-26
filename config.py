import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    MYSQL_HOST = os.environ.get('MYSQL_HOST') 
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER') 
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') 
    MYSQL_DB = os.environ.get('MYSQL_DB') 
    
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    MAIL_SERVER = os.environ.get('MAIL_SERVER') 
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') 
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') 