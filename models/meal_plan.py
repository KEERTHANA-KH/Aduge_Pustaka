from database.mysql_setup import get_connection
from models.recipe import Recipe

class MealPlan:
    def __init__(self, id, user_id, week_start_date, created_at=None):
        self.id = id
        self.user_id = user_id
        self.week_start_date = week_start_date
        self.created_at = created_at
        self.items = []
    
    @staticmethod
    def get_by_user(user_id, week_start_date=None):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        if week_start_date:
            cursor.execute(
                "SELECT * FROM meal_plans WHERE user_id = %s AND week_start_date = %s",
                (user_id, week_start_date)
            )
        else:
            cursor.execute(
                "SELECT * FROM meal_plans WHERE user_id = %s ORDER BY week_start_date DESC",
                (user_id,)
            )
        
        meal_plans = []
        for plan_data in cursor.fetchall():
            plan = MealPlan(
                id=plan_data['id'],
                user_id=plan_data['user_id'],
                week_start_date=plan_data['week_start_date'],
                created_at=plan_data['created_at']
            )
            
            # Get meal plan items
            cursor.execute(
                "SELECT * FROM meal_plan_items WHERE meal_plan_id = %s",
                (plan.id,)
            )
            
            for item_data in cursor.fetchall():
                # Get recipe details
                recipe = Recipe.get_by_id(item_data['recipe_id'])
                
                if recipe:
                    plan.items.append({
                        'id': item_data['id'],
                        'day_of_week': item_data['day_of_week'],
                        'meal_type': item_data['meal_type'],
                        'recipe': recipe
                    })
            
            meal_plans.append(plan)
        
        cursor.close()
        return meal_plans
    
    @staticmethod
    def get_by_id(plan_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM meal_plans WHERE id = %s", (plan_id,))
        plan_data = cursor.fetchone()
        
        if not plan_data:
            cursor.close()
            return None
        
        plan = MealPlan(
            id=plan_data['id'],
            user_id=plan_data['user_id'],
            week_start_date=plan_data['week_start_date'],
            created_at=plan_data['created_at']
        )
        
        # Get meal plan items
        cursor.execute(
            "SELECT * FROM meal_plan_items WHERE meal_plan_id = %s",
            (plan.id,)
        )
        
        for item_data in cursor.fetchall():
            # Get recipe details
            recipe = Recipe.get_by_id(item_data['recipe_id'])
            
            if recipe:
                plan.items.append({
                    'id': item_data['id'],
                    'day_of_week': item_data['day_of_week'],
                    'meal_type': item_data['meal_type'],
                    'recipe': recipe
                })
        
        cursor.close()
        return plan
    
    @staticmethod
    def create(user_id, week_start_date):
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO meal_plans (user_id, week_start_date) VALUES (%s, %s)",
                (user_id, week_start_date)
            )
            conn.commit()
            plan_id = cursor.lastrowid
            cursor.close()
            
            return MealPlan.get_by_id(plan_id)
        except Exception as e:
            conn.rollback()
            cursor.close()
            print(f"Error creating meal plan: {e}")
            return None
    
    @staticmethod
    def add_item(plan_id, recipe_id, day_of_week, meal_type):
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                INSERT INTO meal_plan_items 
                (meal_plan_id, recipe_id, day_of_week, meal_type) 
                VALUES (%s, %s, %s, %s)
                """,
                (plan_id, recipe_id, day_of_week, meal_type)
            )
            conn.commit()
            cursor.close()
            
            return MealPlan.get_by_id(plan_id)
        except Exception as e:
            conn.rollback()
            cursor.close()
            print(f"Error adding meal plan item: {e}")
            return None
    
    @staticmethod
    def remove_item(item_id):
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Get meal plan id first
            cursor.execute(
                "SELECT meal_plan_id FROM meal_plan_items WHERE id = %s",
                (item_id,)
            )
            result = cursor.fetchone()
            if not result:
                cursor.close()
                return None
            
            plan_id = result[0]
            
            # Delete the item
            cursor.execute("DELETE FROM meal_plan_items WHERE id = %s", (item_id,))
            conn.commit()
            cursor.close()
            
            return MealPlan.get_by_id(plan_id)
        except Exception as e:
            conn.rollback()
            cursor.close()
            print(f"Error removing meal plan item: {e}")
            return None