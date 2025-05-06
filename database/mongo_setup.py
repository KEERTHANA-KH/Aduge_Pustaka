from flask import Flask
from pymongo import MongoClient
import json
import os

mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["cookbookit"]

def init_mongo(app: Flask):
    global mongo_client, mongo_db
    mongo_client = MongoClient(app.config['MONGO_URI'])
    mongo_db = mongo_client.get_database()

    # Register the MongoDB instance with Flask app
    app.extensions['mongo_db'] = mongo_db
    
    # Seed recipes and ingredients if the collections are empty
    if mongo_db.recipes.count_documents({}) == 0:
        seed_recipes()
    
    if mongo_db.ingredients.count_documents({}) == 0:
        seed_ingredients()
    
    return mongo_db

def seed_recipes():
    global mongo_db
    recipes = [
        {
            "name": "Spaghetti Carbonara",
            "description": "Classic Italian pasta dish with eggs, cheese, pancetta and black pepper.",
            "ingredients": [
                {"name": "spaghetti", "amount": 400, "unit": "g"},
                {"name": "pancetta", "amount": 150, "unit": "g"},
                {"name": "egg", "amount": 3, "unit": "whole"},
                {"name": "parmesan cheese", "amount": 50, "unit": "g"},
                {"name": "black pepper", "amount": 2, "unit": "tsp"},
                {"name": "salt", "amount": 1, "unit": "tsp"}
            ],
            "instructions": [
                "Boil spaghetti in salted water until al dente.",
                "Fry pancetta until crispy.",
                "Beat eggs with grated parmesan cheese.",
                "Drain pasta and mix with pancetta.",
                "Quickly stir in egg mixture off the heat to create a creamy sauce.",
                "Season with black pepper and serve immediately."
            ],
            "prep_time": 10,
            "cook_time": 15,
            "servings": 4,
            "difficulty": "Medium",
            "tags": ["italian", "pasta", "quick", "dinner"],
            "dietary_info": {
                "vegetarian": False,
                "vegan": False,
                "gluten_free": False,
                "dairy_free": False
            },
            "nutrition": {
                "calories": 450,
                "protein": 20,
                "carbs": 55,
                "fat": 18
            },
            "image_url": "https://images.pexels.com/photos/6287447/pexels-photo-6287447.jpeg"
        },
        {
            "name": "Vegetable Stir Fry",
            "description": "Quick and healthy vegetable stir fry with a savory sauce.",
            "ingredients": [
                {"name": "broccoli", "amount": 1, "unit": "head"},
                {"name": "carrot", "amount": 2, "unit": "whole"},
                {"name": "bell pepper", "amount": 1, "unit": "whole"},
                {"name": "onion", "amount": 1, "unit": "whole"},
                {"name": "garlic", "amount": 2, "unit": "cloves"},
                {"name": "soy sauce", "amount": 2, "unit": "tbsp"},
                {"name": "sesame oil", "amount": 1, "unit": "tbsp"},
                {"name": "rice", "amount": 2, "unit": "cups"}
            ],
            "instructions": [
                "Chop all vegetables into bite-sized pieces.",
                "Heat oil in a wok or large frying pan.",
                "Add garlic and onion, stir fry until fragrant.",
                "Add remaining vegetables and stir fry until crisp-tender.",
                "Add soy sauce and sesame oil, toss to combine.",
                "Serve hot over cooked rice."
            ],
            "prep_time": 15,
            "cook_time": 10,
            "servings": 4,
            "difficulty": "Easy",
            "tags": ["vegetarian", "asian", "quick", "healthy"],
            "dietary_info": {
                "vegetarian": True,
                "vegan": True,
                "gluten_free": False,
                "dairy_free": True
            },
            "nutrition": {
                "calories": 320,
                "protein": 8,
                "carbs": 60,
                "fat": 6
            },
            "image_url": "https://images.pexels.com/photos/1640774/pexels-photo-1640774.jpeg"
        },
        {
            "name": "Avocado Toast",
            "description": "Simple and nutritious breakfast with avocado on toast.",
            "ingredients": [
                {"name": "bread", "amount": 2, "unit": "slices"},
                {"name": "avocado", "amount": 1, "unit": "whole"},
                {"name": "lemon juice", "amount": 1, "unit": "tsp"},
                {"name": "salt", "amount": 0.5, "unit": "tsp"},
                {"name": "red pepper flakes", "amount": 0.25, "unit": "tsp"},
                {"name": "egg", "amount": 2, "unit": "whole"}
            ],
            "instructions": [
                "Toast bread until golden and crisp.",
                "Mash avocado with lemon juice and salt.",
                "Fry eggs sunny-side up.",
                "Spread avocado mixture on toast.",
                "Top with fried egg and sprinkle with red pepper flakes."
            ],
            "prep_time": 5,
            "cook_time": 5,
            "servings": 2,
            "difficulty": "Easy",
            "tags": ["breakfast", "vegetarian", "quick", "healthy"],
            "dietary_info": {
                "vegetarian": True,
                "vegan": False,
                "gluten_free": False,
                "dairy_free": True
            },
            "nutrition": {
                "calories": 280,
                "protein": 10,
                "carbs": 20,
                "fat": 18
            },
            "image_url": "https://images.pexels.com/photos/704569/pexels-photo-704569.jpeg"
        },
        {
            "name": "Vegetarian Chili",
            "description": "Hearty and flavorful vegetarian chili with beans and vegetables.",
            "ingredients": [
                {"name": "kidney beans", "amount": 400, "unit": "g"},
                {"name": "black beans", "amount": 400, "unit": "g"},
                {"name": "onion", "amount": 1, "unit": "large"},
                {"name": "bell pepper", "amount": 2, "unit": "whole"},
                {"name": "garlic", "amount": 3, "unit": "cloves"},
                {"name": "diced tomatoes", "amount": 800, "unit": "g"},
                {"name": "tomato paste", "amount": 2, "unit": "tbsp"},
                {"name": "chili powder", "amount": 2, "unit": "tbsp"},
                {"name": "cumin", "amount": 1, "unit": "tbsp"},
                {"name": "paprika", "amount": 1, "unit": "tsp"}
            ],
            "instructions": [
                "Dice onion and bell peppers, mince garlic.",
                "Sauté onion, bell peppers, and garlic until soft.",
                "Add spices and cook until fragrant.",
                "Add beans, diced tomatoes, and tomato paste.",
                "Simmer for 30 minutes, stirring occasionally.",
                "Serve hot with optional toppings like cheese, sour cream, or avocado."
            ],
            "prep_time": 15,
            "cook_time": 40,
            "servings": 6,
            "difficulty": "Medium",
            "tags": ["vegetarian", "dinner", "healthy", "meal prep"],
            "dietary_info": {
                "vegetarian": True,
                "vegan": True,
                "gluten_free": True,
                "dairy_free": True
            },
            "nutrition": {
                "calories": 320,
                "protein": 15,
                "carbs": 55,
                "fat": 4
            },
            "image_url": "https://images.pexels.com/photos/4202392/pexels-photo-4202392.jpeg"
        },
        {
            "name": "Chicken Salad",
            "description": "Fresh and protein-packed chicken salad with mixed greens and homemade dressing.",
            "ingredients": [
                {"name": "chicken breast", "amount": 2, "unit": "whole"},
                {"name": "mixed greens", "amount": 200, "unit": "g"},
                {"name": "cherry tomatoes", "amount": 100, "unit": "g"},
                {"name": "cucumber", "amount": 1, "unit": "whole"},
                {"name": "red onion", "amount": 0.5, "unit": "whole"},
                {"name": "olive oil", "amount": 2, "unit": "tbsp"},
                {"name": "lemon juice", "amount": 1, "unit": "tbsp"},
                {"name": "mustard", "amount": 1, "unit": "tsp"},
                {"name": "honey", "amount": 1, "unit": "tsp"},
                {"name": "salt", "amount": 0.5, "unit": "tsp"},
                {"name": "black pepper", "amount": 0.25, "unit": "tsp"}
            ],
            "instructions": [
                "Season chicken breasts with salt and pepper and grill until cooked through.",
                "Wash and prep all vegetables.",
                "Slice cucumber and red onion, halve cherry tomatoes.",
                "Whisk together olive oil, lemon juice, mustard, honey, salt, and pepper for the dressing.",
                "Slice cooled chicken breast.",
                "Combine all ingredients in a large bowl, drizzle with dressing, and toss gently."
            ],
            "prep_time": 15,
            "cook_time": 15,
            "servings": 2,
            "difficulty": "Easy",
            "tags": ["salad", "protein", "healthy", "lunch"],
            "dietary_info": {
                "vegetarian": False,
                "vegan": False,
                "gluten_free": True,
                "dairy_free": True
            },
            "nutrition": {
                "calories": 350,
                "protein": 30,
                "carbs": 15,
                "fat": 18
            },
            "image_url": "https://images.pexels.com/photos/5938/food-salad-healthy-lunch.jpg"
        }
    ]

    mongo_db.recipes.insert_many(recipes)

def seed_ingredients():
    global mongo_db
    ingredients = [
        {"name": "spaghetti", "category": "pasta", "unit": "g"},
        {"name": "pancetta", "category": "meat", "unit": "g"},
        {"name": "egg", "category": "dairy", "unit": "whole"},
        {"name": "parmesan cheese", "category": "dairy", "unit": "g"},
        {"name": "black pepper", "category": "spice", "unit": "tsp"},
        {"name": "salt", "category": "spice", "unit": "tsp"},
        {"name": "broccoli", "category": "vegetable", "unit": "head"},
        {"name": "carrot", "category": "vegetable", "unit": "whole"},
        {"name": "bell pepper", "category": "vegetable", "unit": "whole"},
        {"name": "onion", "category": "vegetable", "unit": "whole"},
        {"name": "garlic", "category": "vegetable", "unit": "cloves"},
        {"name": "soy sauce", "category": "condiment", "unit": "tbsp"},
        {"name": "sesame oil", "category": "oil", "unit": "tbsp"},
        {"name": "rice", "category": "grain", "unit": "cups"},
        {"name": "bread", "category": "bakery", "unit": "slices"},
        {"name": "avocado", "category": "fruit", "unit": "whole"},
        {"name": "lemon juice", "category": "condiment", "unit": "tsp"},
        {"name": "red pepper flakes", "category": "spice", "unit": "tsp"},
        {"name": "kidney beans", "category": "canned goods", "unit": "g"},
        {"name": "black beans", "category": "canned goods", "unit": "g"},
        {"name": "diced tomatoes", "category": "canned goods", "unit": "g"},
        {"name": "tomato paste", "category": "canned goods", "unit": "tbsp"},
        {"name": "chili powder", "category": "spice", "unit": "tbsp"},
        {"name": "cumin", "category": "spice", "unit": "tbsp"},
        {"name": "paprika", "category": "spice", "unit": "tsp"},
        {"name": "chicken breast", "category": "meat", "unit": "whole"},
        {"name": "mixed greens", "category": "vegetable", "unit": "g"},
        {"name": "cherry tomatoes", "category": "vegetable", "unit": "g"},
        {"name": "cucumber", "category": "vegetable", "unit": "whole"},
        {"name": "red onion", "category": "vegetable", "unit": "whole"},
        {"name": "olive oil", "category": "oil", "unit": "tbsp"},
        {"name": "mustard", "category": "condiment", "unit": "tsp"},
        {"name": "honey", "category": "sweetener", "unit": "tsp"}
    ]

    mongo_db.ingredients.insert_many(ingredients)