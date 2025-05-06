from database.mysql_setup import get_connection
from models.recipe import Recipe
from models.inventory import Inventory
from datetime import datetime

class CompletedRecipe:
    def __init__(self, id, user_id, recipe_id, completed_date, servings_made):
        self.id = id
        self.user_id = user_id
        self.recipe_id = recipe_id
        self.completed_date = completed_date
        self.servings_made = servings_made
        self.recipe = None
    
    @staticmethod
    def get_by_user(user_id, limit=10):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            """
            SELECT * FROM completed_recipes 
            WHERE user_id = %s 
            ORDER BY completed_date DESC
            LIMIT %s
            """,
            (user_id, limit)
        )
        
        completed_recipes = []
        for data in cursor.fetchall():
            completed = CompletedRecipe(
                id=data['id'],
                user_id=data['user_id'],
                recipe_id=data['recipe_id'],
                completed_date=data['completed_date'],
                servings_made=data['servings_made']
            )
            
            # Get recipe details
            recipe = Recipe.get_by_id(data['recipe_id'])
            if recipe:
                completed.recipe = recipe
            
            completed_recipes.append(completed)
        
        cursor.close()
        return completed_recipes
    
    @staticmethod
    def mark_completed(user_id, recipe_id, servings_made=1):
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """
                INSERT INTO completed_recipes 
                (user_id, recipe_id, servings_made) 
                VALUES (%s, %s, %s)
                """,
                (user_id, recipe_id, servings_made)
            )
            conn.commit()
            completed_id = cursor.lastrowid
            cursor.close()
            
            # Update inventory based on recipe ingredients used
            CompletedRecipe.update_inventory(user_id, recipe_id, servings_made)
            
            return completed_id
        except Exception as e:
            conn.rollback()
            cursor.close()
            print(f"Error marking recipe as completed: {e}")
            return None
    
    @staticmethod
    def update_inventory(user_id, recipe_id, servings_made):
        # Get recipe details
        recipe = Recipe.get_by_id(recipe_id)
        if not recipe:
            return False
        
        # Get recipe ingredients
        ingredients = recipe.get('ingredients', [])
        recipe_servings = recipe.get('servings', 1)
        
        # Calculate ingredient amounts based on servings made
        for ingredient in ingredients:
            ingredient_name = ingredient.get('name')
            amount = ingredient.get('amount', 0)
            
            # Calculate amount used based on servings
            if recipe_servings > 0:
                amount_used = (amount / recipe_servings) * servings_made
                
                # Decrease inventory (negative value because we're removing)
                Inventory.update_quantity(user_id, ingredient_name, -amount_used)
        
        return True