from database.mongo_setup import mongo_db
from bson.objectid import ObjectId

print(f"Mongo DB connected: {mongo_db is not None}")

class Recipe:
    @staticmethod
    def get_all():
        return list(mongo_db.recipes.find())
    
    @staticmethod
    def get_by_id(recipe_id):
        try:
            return mongo_db.recipes.find_one({"_id": ObjectId(recipe_id)})
        except:
            return None
    
    @staticmethod
    def search_by_ingredients(ingredients_list, exclude_ingredients=None):
        """
        Search for recipes that can be made with the given ingredients
        
        Args:
            ingredients_list (list): List of ingredients names
            exclude_ingredients (list, optional): List of ingredients to exclude
            
        Returns:
            list: List of recipes that can be made with the given ingredients
        """
        if not ingredients_list:
            return []
        
        # Create query to match recipes with ingredients from the list
        query = {
            "ingredients.name": {
                "$in": ingredients_list
            }
        }
        
        # Add exclusion if provided
        if exclude_ingredients:
            query["ingredients.name"] = {
                "$nin": exclude_ingredients
            }
        
        # Find recipes and calculate match percentage
        recipes = list(mongo_db.recipes.find(query))
        
        # Calculate match percentage for each recipe
        for recipe in recipes:
            total_ingredients = len(recipe["ingredients"])
            matching_ingredients = sum(1 for i in recipe["ingredients"] if i["name"] in ingredients_list)
            recipe["match_percentage"] = (matching_ingredients / total_ingredients) * 100
        
        # Sort by match percentage (highest first)
        recipes.sort(key=lambda x: x.get("match_percentage", 0), reverse=True)
        
        return recipes
    
    @staticmethod
    def filter_by_dietary(recipes, dietary_filters):
        """
        Filter recipes based on dietary preferences
        
        Args:
            recipes (list): List of recipes to filter
            dietary_filters (dict): Dictionary of dietary filters
            
        Returns:
            list: Filtered list of recipes
        """
        if not dietary_filters:
            return recipes
        
        filtered_recipes = []
        
        for recipe in recipes:
            # Check if recipe matches all dietary filters
            matches_all = True
            
            for key, value in dietary_filters.items():
                if value and recipe.get("dietary_info", {}).get(key) != value:
                    matches_all = False
                    break
            
            if matches_all:
                filtered_recipes.append(recipe)
        
        return filtered_recipes
    
    @staticmethod
    def search_by_name(search_term):
        """
        Search for recipes by name
        
        Args:
            search_term (str): Term to search for
            
        Returns:
            list: List of recipes matching the search term
        """
        if not search_term:
            return []
        
        # Create text index if it doesn't exist
        if "name_text" not in mongo_db.recipes.index_information():
            mongo_db.recipes.create_index([("name", "text"), ("description", "text")])
        
        return list(mongo_db.recipes.find({"$text": {"$search": search_term}}))
    
    @staticmethod
    def get_recipe_ingredients(recipe_id):
        """
        Get ingredients for a specific recipe
        
        Args:
            recipe_id (str): Recipe ID
            
        Returns:
            list: List of ingredients for the recipe
        """
        recipe = Recipe.get_by_id(recipe_id)
        if not recipe:
            return []
        
        return recipe.get("ingredients", [])