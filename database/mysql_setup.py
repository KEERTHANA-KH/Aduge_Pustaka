import mysql.connector
from mysql.connector import Error
from config import Config

mysql_connection = None

def init_mysql(app):
    global mysql_connection
    try:
        mysql_connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD']
        )
        
        # Create database if it doesn't exist
        cursor = mysql_connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {app.config['MYSQL_DB']}")
        cursor.execute(f"USE {app.config['MYSQL_DB']}")
        cursor.close()
        
        return mysql_connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def get_connection():
    global mysql_connection
    if mysql_connection is None or not mysql_connection.is_connected():
        mysql_connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB
        )
    return mysql_connection

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) NOT NULL UNIQUE,
        email VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create Inventory table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        ingredient_name VARCHAR(100) NOT NULL,
        category VARCHAR(50) NOT NULL,
        quantity FLOAT NOT NULL,
        unit VARCHAR(20) NOT NULL,
        expiry_date DATE,
        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    # Create User Preferences table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_preferences (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL UNIQUE,
        is_vegetarian BOOLEAN DEFAULT FALSE,
        is_vegan BOOLEAN DEFAULT FALSE,
        is_gluten_free BOOLEAN DEFAULT FALSE,
        is_dairy_free BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    # Create Meal Plans table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meal_plans (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        week_start_date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    # Create Meal Plan Items table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meal_plan_items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        meal_plan_id INT NOT NULL,
        recipe_id VARCHAR(24) NOT NULL,
        day_of_week INT NOT NULL, 
        meal_type VARCHAR(20) NOT NULL,
        FOREIGN KEY (meal_plan_id) REFERENCES meal_plans(id) ON DELETE CASCADE
    )
    """)
    
    # Create Completed Recipes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS completed_recipes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        recipe_id VARCHAR(24) NOT NULL,
        completed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        servings_made INT NOT NULL DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    conn.commit()
    cursor.close()