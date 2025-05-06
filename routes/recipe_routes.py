from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from models.recipe import Recipe
from models.inventory import Inventory
from models.completed_recipe import CompletedRecipe
from database.mysql_setup import get_connection

recipe_bp = Blueprint('recipe', __name__, url_prefix='/recipe')

@recipe_bp.route('/')
@login_required
def index():
    # Get user's inventory ingredients
    inventory_items = Inventory.get_by_user_id(current_user.id)
    ingredient_names = [item.ingredient_name for item in inventory_items]
    
    # Get recipes that can be made with these ingredients
    recipes = Recipe.search_by_ingredients(ingredient_names)
    
    # Get user's dietary preferences
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_preferences WHERE user_id = %s", (current_user.id,))
    preferences = cursor.fetchone()
    cursor.close()
    
    # Apply dietary filters if user has preferences
    if preferences:
        dietary_filters = {
            'vegetarian': preferences['is_vegetarian'],
            'vegan': preferences['is_vegan'],
            'gluten_free': preferences['is_gluten_free'],
            'dairy_free': preferences['is_dairy_free']
        }
        # Only apply filters that are true
        active_filters = {k: v for k, v in dietary_filters.items() if v}
        
        if active_filters:
            recipes = Recipe.filter_by_dietary(recipes, active_filters)
    
    # Get recently completed recipes
    completed_recipes = CompletedRecipe.get_by_user(current_user.id, limit=5)
    
    return render_template('recipe/index.html', 
                          recipes=recipes, 
                          completed_recipes=completed_recipes,
                          inventory_count=len(inventory_items))

@recipe_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    search_term = request.args.get('term', '')
    
    if search_term:
        recipes = Recipe.search_by_name(search_term)
    else:
        recipes = Recipe.get_all()
    
    # Get user's dietary preferences
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_preferences WHERE user_id = %s", (current_user.id,))
    preferences = cursor.fetchone()
    cursor.close()
    
    # Apply filters from form
    vegetarian = request.args.get('vegetarian') == 'on'
    vegan = request.args.get('vegan') == 'on'
    gluten_free = request.args.get('gluten_free') == 'on'
    dairy_free = request.args.get('dairy_free') == 'on'
    
    # Create dietary filters dict
    dietary_filters = {}
    if vegetarian:
        dietary_filters['vegetarian'] = True
    if vegan:
        dietary_filters['vegan'] = True
    if gluten_free:
        dietary_filters['gluten_free'] = True
    if dairy_free:
        dietary_filters['dairy_free'] = True
    
    # Apply dietary filters if any are selected
    if dietary_filters:
        recipes = Recipe.filter_by_dietary(recipes, dietary_filters)
    
    return render_template('recipe/search.html', 
                          recipes=recipes, 
                          search_term=search_term,
                          preferences=preferences)

@recipe_bp.route('/<recipe_id>')
@login_required
def detail(recipe_id):
    recipe = Recipe.get_by_id(recipe_id)
    
    if not recipe:
        flash('Recipe not found.', 'danger')
        return redirect(url_for('recipe.index'))
    
    # Check if user has the ingredients
    inventory_items = Inventory.get_by_user_id(current_user.id)
    user_ingredients = {item.ingredient_name: {'quantity': item.quantity, 'unit': item.unit} 
                      for item in inventory_items}
    
    has_all_ingredients = True
    missing_ingredients = []
    
    for ingredient in recipe.get('ingredients', []):
        name = ingredient.get('name')
        amount = ingredient.get('amount', 0)
        unit = ingredient.get('unit', '')
        
        if name not in user_ingredients:
            has_all_ingredients = False
            missing_ingredients.append({
                'name': name,
                'amount': amount,
                'unit': unit
            })
        elif user_ingredients[name]['quantity'] < amount:
            has_all_ingredients = False
            missing_ingredients.append({
                'name': name,
                'amount': amount - user_ingredients[name]['quantity'],
                'unit': unit
            })
    
    return render_template('recipe/detail.html', 
                          recipe=recipe, 
                          has_all_ingredients=has_all_ingredients,
                          missing_ingredients=missing_ingredients)

@recipe_bp.route('/<recipe_id>/complete', methods=['POST'])
@login_required
def complete(recipe_id):
    recipe = Recipe.get_by_id(recipe_id)
    
    if not recipe:
        flash('Recipe not found.', 'danger')
        return redirect(url_for('recipe.index'))
    
    servings = int(request.form.get('servings', 1))
    
    # Mark recipe as completed
    completed_id = CompletedRecipe.mark_completed(current_user.id, recipe_id, servings)
    
    if completed_id:
        flash('Recipe marked as completed and inventory updated!', 'success')
    else:
        flash('Error marking recipe as completed.', 'danger')
    
    return redirect(url_for('recipe.detail', recipe_id=recipe_id))

@recipe_bp.route('/completed')
@login_required
def completed():
    completed_recipes = CompletedRecipe.get_by_user(current_user.id)
    return render_template('recipe/completed.html', completed_recipes=completed_recipes)

@recipe_bp.route('/api/can-make', methods=['GET'])
@login_required
def api_can_make():
    # Get user's inventory ingredients
    inventory_items = Inventory.get_by_user_id(current_user.id)
    ingredient_names = [item.ingredient_name for item in inventory_items]
    
    # Get recipes that can be made with these ingredients
    recipes = Recipe.search_by_ingredients(ingredient_names)
    
    # Format for JSON response
    recipes_list = []
    for recipe in recipes:
        recipes_list.append({
            'id': str(recipe['_id']),
            'name': recipe['name'],
            'match_percentage': recipe.get('match_percentage', 0)
        })
    
    return jsonify({'recipes': recipes_list})




