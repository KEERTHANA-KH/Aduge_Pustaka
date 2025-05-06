from flask_login import UserMixin
import bcrypt
from database.mysql_setup import get_connection

class User(UserMixin):
    def __init__(self, id, username, email, password=None):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
    
    def get_id(self):
        return str(self.id)
    
    @staticmethod
    def get_by_id(user_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        cursor.close()
        
        if not user_data:
            return None
        
        return User(
            id=user_data['id'],
            username=user_data['username'],
            email=user_data['email']
        )
    
    @staticmethod
    def get_by_email(email):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        cursor.close()
        
        if not user_data:
            return None
        
        return User(
            id=user_data['id'],
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password']
        )
    
    @staticmethod
    def create(username, email, password):
        conn = get_connection()
        cursor = conn.cursor()
        
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_password.decode('utf-8'))
            )
            conn.commit()
            user_id = cursor.lastrowid
            cursor.close()
            
            # Create default user preferences
            User.create_default_preferences(user_id)
            
            return User.get_by_id(user_id)
        except Exception as e:
            conn.rollback()
            cursor.close()
            print(f"Error creating user: {e}")
            return None
    
    @staticmethod
    def create_default_preferences(user_id):
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO user_preferences (user_id) VALUES (%s)",
                (user_id,)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error creating user preferences: {e}")
        finally:
            cursor.close()
    
    @staticmethod
    def verify_password(user, password):
        if not user or not user.password:
            return False
        
        return bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8'))