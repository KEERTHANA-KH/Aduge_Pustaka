from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from models.meal_plan import MealPlan
from models.recipe import Recipe
from models.inventory import Inventory
from datetime import datetime, timedelta
from database.mysql_setup import get_connection

meal_plan_bp = Blueprint('meal_plan', __name__, url_prefix='/meal-plan')

@meal_plan_bp.route('/')
@login_required
def index():
    # Determine the current week's start date (Monday)
    today = datetime.now().date()
    days_since_monday = today.weekday()
    week_start_date = today - timedelta(days=days_since_monday)
    
    # Get meal plans for current week
    meal_plans = MealPlan.get_by_user(current_user.id, week_start_date)
    
    # If no meal plan exists for this week, create one
    if not meal_plans:
        meal_plan = MealPlan.create(current_user.id, week_start_date)
        meal_plans = [meal_plan] if meal_plan else []
    
    # Get user's inventory ingredients for recipe suggestions
    inventory_items = Inventory.get_by_user_id(current_user.id)
    ingredient_names = [item.ingredient_name for item in inventory_items]
    
    # Get recipe suggestions based on inventory
    recipe_suggestions = Recipe.search_by_ingredients(ingredient_names)
    
    # Apply dietary preferences to suggestions
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_preferences WHERE user_id = %s", (current_user.id,))
    preferences = cursor.fetchone()
    cursor.close()
    
    if preferences and any([preferences['is_vegetarian'], preferences['is_vegan'], 
                           preferences['is_gluten_free'], preferences['is_dairy_free']]):
        dietary_filters = {
            'vegetarian': preferences['is_vegetarian'],
            'vegan': preferences['is_vegan'],
            'gluten_free': preferences['is_gluten_free'],
            'dairy_free': preferences['is_dairy_free']
        }
        # Only apply filters that are true
        active_filters = {k: v for k, v in dietary_filters.items() if v}
        
        if active_filters:
            recipe_suggestions = Recipe.filter_by_dietary(recipe_suggestions, active_filters)
    
    # Limit to top 10 suggestions
    recipe_suggestions = recipe_suggestions[:10]
    
    return render_template('meal_plan/index.html', 
                          meal_plans=meal_plans, 
                          week_start_date=week_start_date,
                          recipe_suggestions=recipe_suggestions)

@meal_plan_bp.route('/add', methods=['POST'])
@login_required
def add_recipe():
    plan_id = request.form.get('plan_id')
    recipe_id = request.form.get('recipe_id')
    day_of_week = int(request.form.get('day_of_week'))
    meal_type = request.form.get('meal_type')
    
    if not all([plan_id, recipe_id, day_of_week, meal_type]):
        flash('Missing required fields.', 'danger')
        return redirect(url_for('meal_plan.index'))
    
    # Add recipe to meal plan
    updated_plan = MealPlan.add_item(plan_id, recipe_id, day_of_week, meal_type)
    
    if updated_plan:
        flash('Recipe added to meal plan!', 'success')
    else:
        flash('Error adding recipe to meal plan.', 'danger')
    
    return redirect(url_for('meal_plan.index'))

@meal_plan_bp.route('/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_recipe(item_id):
    # Remove recipe from meal plan
    updated_plan = MealPlan.remove_item(item_id)
    
    if updated_plan:
        flash('Recipe removed from meal plan!', 'success')
    else:
        flash('Error removing recipe from meal plan.', 'danger')
    
    return redirect(url_for('meal_plan.index'))

@meal_plan_bp.route('/generate', methods=['GET'])
@login_required
def generate_plan():
    # Get the meal plan ID from the query string
    plan_id = request.args.get('plan_id')
    
    if not plan_id:
        flash('No meal plan specified.', 'danger')
        return redirect(url_for('meal_plan.index'))
    
    # Get user's inventory ingredients
    inventory_items = Inventory.get_by_user_id(current_user.id)
    ingredient_names = [item.ingredient_name for item in inventory_items]
    
    # Get recipes that can be made with user's ingredients
    available_recipes = Recipe.search_by_ingredients(ingredient_names)
    
    # Apply dietary preferences
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_preferences WHERE user_id = %s", (current_user.id,))
    preferences = cursor.fetchone()
    cursor.close()
    
    if preferences and any([preferences['is_vegetarian'], preferences['is_vegan'], 
                           preferences['is_gluten_free'], preferences['is_dairy_free']]):
        dietary_filters = {
            'vegetarian': preferences['is_vegetarian'],
            'vegan': preferences['is_vegan'],
            'gluten_free': preferences['is_gluten_free'],
            'dairy_free': preferences['is_dairy_free']
        }
        # Only apply filters that are true
        active_filters = {k: v for k, v in dietary_filters.items() if v}
        
        if active_filters:
            available_recipes = Recipe.filter_by_dietary(available_recipes, active_filters)
    
    # Generate a meal plan (simple version - just assign random recipes)
    # In a real app, this would be more sophisticated
    meal_types = ['breakfast', 'lunch', 'dinner']
    
    if len(available_recipes) < 3:
        flash('Not enough recipes available to generate a meal plan.', 'warning')
        return redirect(url_for('meal_plan.index'))
    
    # Clear existing meal plan
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM meal_plan_items WHERE meal_plan_id = %s", (plan_id,))
    conn.commit()
    cursor.close()
    
    # Add recipes to meal plan for each day of the week
    for day in range(7):  # 0-6 for Monday to Sunday
        for meal_type in meal_types:
            # Pick a random recipe that matches the criteria
            import random
            recipe = random.choice(available_recipes)
            
            # Add to meal plan
            MealPlan.add_item(plan_id, str(recipe['_id']), day, meal_type)
    
    flash('Meal plan generated successfully!', 'success')
    return redirect(url_for('meal_plan.index'))

@meal_plan_bp.route('/grocery-list')
@login_required
def grocery_list():
    # Get the current meal plan
    today = datetime.now().date()
    days_since_monday = today.weekday()
    week_start_date = today - timedelta(days=days_since_monday)
    
    meal_plans = MealPlan.get_by_user(current_user.id, week_start_date)
    
    if not meal_plans:
        flash('No meal plan found for this week.', 'warning')
        return redirect(url_for('meal_plan.index'))
    
    meal_plan = meal_plans[0]
    
    # Get user's inventory
    inventory_items = Inventory.get_by_user_id(current_user.id)
    user_ingredients = {item.ingredient_name: {'quantity': item.quantity, 'unit': item.unit} 
                      for item in inventory_items}
    
    # Compile grocery list from meal plan
    grocery_list = {}
    
    for item in meal_plan.items:
        recipe = item['recipe']
        
        for ingredient in recipe.get('ingredients', []):
            name = ingredient.get('name')
            amount = ingredient.get('amount', 0)
            unit = ingredient.get('unit', '')
            
            # Check if user already has this ingredient
            if name in user_ingredients:
                # If user has enough, skip
                if user_ingredients[name]['quantity'] >= amount:
                    continue
                # Otherwise, add the difference
                needed_amount = amount - user_ingredients[name]['quantity']
            else:
                needed_amount = amount
            
            # Add to grocery list
            if name in grocery_list:
                if grocery_list[name]['unit'] == unit:
                    grocery_list[name]['amount'] += needed_amount
                else:
                    # If units don't match, keep them separate
                    alt_key = f"{name} ({unit})"
                    if alt_key in grocery_list:
                        grocery_list[alt_key]['amount'] += needed_amount
                    else:
                        grocery_list[alt_key] = {
                            'name': name,
                            'amount': needed_amount,
                            'unit': unit
                        }
            else:
                grocery_list[name] = {
                    'name': name,
                    'amount': needed_amount,
                    'unit': unit
                }
    
    return render_template('meal_plan/grocery_list.html', 
                          grocery_list=grocery_list.values(),
                          meal_plan=meal_plan)