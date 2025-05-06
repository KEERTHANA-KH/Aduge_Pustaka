from database.mysql_setup import get_connection
from datetime import datetime, timedelta
from config import Config

class Inventory:
    def __init__(self, id, user_id, ingredient_name, category, quantity, unit, expiry_date=None, added_date=None):
        self.id = id
        self.user_id = user_id
        self.ingredient_name = ingredient_name
        self.category = category
        self.quantity = quantity
        self.unit = unit
        self.expiry_date = expiry_date
        self.added_date = added_date
    
    @staticmethod
    def get_by_user_id(user_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT * FROM inventory WHERE user_id = %s ORDER BY ingredient_name",
            (user_id,)
        )
        
        inventory_items = []
        for item in cursor.fetchall():
            inventory_items.append(Inventory(
                id=item['id'],
                user_id=item['user_id'],
                ingredient_name=item['ingredient_name'],
                category=item['category'],
                quantity=item['quantity'],
                unit=item['unit'],
                expiry_date=item['expiry_date'],
                added_date=item['added_date']
            ))
        
        cursor.close()
        return inventory_items
    
    @staticmethod
    def get_by_id(item_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM inventory WHERE id = %s", (item_id,))
        item = cursor.fetchone()
        cursor.close()
        
        if not item:
            return None
        
        return Inventory(
            id=item['id'],
            user_id=item['user_id'],
            ingredient_name=item['ingredient_name'],
            category=item['category'],
            quantity=item['quantity'],
            unit=item['unit'],
            expiry_date=item['expiry_date'],
            added_date=item['added_date']
        )
    
    @staticmethod
    def add_item(user_id, ingredient_name, category, quantity, unit, expiry_date=None):
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                INSERT INTO inventory 
                (user_id, ingredient_name, category, quantity, unit, expiry_date) 
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (user_id, ingredient_name, category, quantity, unit, expiry_date)
            )
            conn.commit()
            item_id = cursor.lastrowid
            cursor.close()
            
            return Inventory.get_by_id(item_id)
        except Exception as e:
            conn.rollback()
            cursor.close()
            print(f"Error adding inventory item: {e}")
            return None
    
    @staticmethod
    def update_item(item_id, ingredient_name, category, quantity, unit, expiry_date=None):
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                UPDATE inventory 
                SET ingredient_name = %s, category = %s, quantity = %s, unit = %s, expiry_date = %s
                WHERE id = %s
                """,
                (ingredient_name, category, quantity, unit, expiry_date, item_id)
            )
            conn.commit()
            cursor.close()
            
            return Inventory.get_by_id(item_id)
        except Exception as e:
            conn.rollback()
            cursor.close()
            print(f"Error updating inventory item: {e}")
            return None
    
    @staticmethod
    def delete_item(item_id):
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM inventory WHERE id = %s", (item_id,))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            conn.rollback()
            cursor.close()
            print(f"Error deleting inventory item: {e}")
            return False
    
    @staticmethod
    def get_expiring_items(user_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        warning_date = datetime.now().date() + timedelta(days=Config.EXPIRATION_WARNING_DAYS)
        
        cursor.execute(
            """
            SELECT * FROM inventory 
            WHERE user_id = %s AND expiry_date IS NOT NULL AND expiry_date <= %s
            ORDER BY expiry_date
            """,
            (user_id, warning_date)
        )
        
        expiring_items = []
        for item in cursor.fetchall():
            expiring_items.append(Inventory(
                id=item['id'],
                user_id=item['user_id'],
                ingredient_name=item['ingredient_name'],
                category=item['category'],
                quantity=item['quantity'],
                unit=item['unit'],
                expiry_date=item['expiry_date'],
                added_date=item['added_date']
            ))
        
        cursor.close()
        return expiring_items
    
    @staticmethod
    def update_quantity(user_id, ingredient_name, quantity_change):
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # First check if the ingredient exists for this user
            cursor.execute(
                "SELECT id, quantity FROM inventory WHERE user_id = %s AND ingredient_name = %s",
                (user_id, ingredient_name)
            )
            
            item = cursor.fetchone()
            
            if item:
                item_id, current_quantity = item
                new_quantity = current_quantity + quantity_change
                
                # If new quantity is 0 or less, delete the item
                if new_quantity <= 0:
                    cursor.execute("DELETE FROM inventory WHERE id = %s", (item_id,))
                else:
                    cursor.execute(
                        "UPDATE inventory SET quantity = %s WHERE id = %s",
                        (new_quantity, item_id)
                    )
                
                conn.commit()
                cursor.close()
                return True
            else:
                cursor.close()
                return False
        except Exception as e:
            conn.rollback()
            cursor.close()
            print(f"Error updating inventory quantity: {e}")
            return False