import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-for-dev')
    
    # MongoDB settings
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/cookbookit')
    
    # MySQL settings
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'root@123')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'cookbookit')
    
    # Application settings
    EXPIRATION_WARNING_DAYS = 3  # Days before expiration to start showing warnings