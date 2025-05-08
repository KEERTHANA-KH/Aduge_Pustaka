# CookBookIt

CookBookIt helps you make the most of your kitchen by generating recipes from available ingredients, tracking expiration dates, and offering meal planning features. It provides nutritional analysis and allows recipe modifications to accommodate dietary restrictions, making it easy to create personalized, healthy meals with what you have on hand.

## Features

- **Recipe Search Based on Inventory**: Find recipes based on ingredients you already have
- **Inventory Management**: Track ingredients with expiration dates and categories
- **Dietary Filtering**: Filter recipes based on dietary preferences (vegetarian, vegan, gluten-free, dairy-free)
- **Real-time Inventory Updates**: Automatically update inventory when recipes are completed
- **Meal Planning**: Create weekly meal plans with suggested recipes
- **Recipe Completion Tracking**: Keep a history of recipes you've made
- **Expiration Notifications**: Get alerts for ingredients nearing expiry
- **Grocery List Generation**: Create shopping lists based on meal plans

## Technology Stack

- **Backend**: Flask (Python)
- **Databases**:
  - MongoDB for recipes and ingredients data
  - MySQL for user accounts, inventory, and preferences
- **Frontend**: HTML, CSS, JavaScript

## Installation

1. Clone the repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Set up MongoDB and MySQL databases
4. Configure the connection details in `.env` file
5. Run the application:
   ```
   python app.py
   ```

## Configuration

Create a `.env` file with the following variables:

```
SECRET_KEY=your_secret_key
MONGO_URI=mongodb://localhost:27017/cookbookit
MYSQL_HOST=localhost
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DB=cookbookit
```

## Project Structure

- `app.py`: Main Flask application
- `config.py`: Configuration settings
- `database/`: Database setup scripts
- `models/`: Database models
- `routes/`: API routes
- `static/`: Static assets (CSS, JS)
- `templates/`: HTML templates

## Usage

1. Register for an account
2. Add ingredients to your inventory
3. Search for recipes based on available ingredients
4. Create meal plans
5. Track completed recipes
6. Generate grocery lists

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.





............................
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
        
        # Get user's inventory
        inventory_items = Inventory.get_by_user_id(user_id)
        inventory_dict = {}
        for item in inventory_items:
            inventory_dict[item.ingredient_name] = {
                'id': item.id,
                'quantity': item.quantity,
                'unit': item.unit,
            }
        
        # Calculate ingredient amounts based on servings made
        for ingredient in ingredients:
            ingredient_name = ingredient.get('name')
            amount = ingredient.get('amount', 0)
            unit = ingredient.get('unit', '')
            
            # Calculate amount used based on servings
            if recipe_servings > 0:
                amount_used = (amount / recipe_servings) * servings_made
                
                # If user has this ingredient, update it
                if ingredient_name in inventory_dict:
                    inventory_item = inventory_dict[ingredient_name]
                    
                    # If units match, simple update
                    if inventory_item['unit'] == unit:
                        Inventory.update_quantity(user_id, ingredient_name, -amount_used)
                    else:
                        # Try to convert units
                        converted = Inventory.convert_units(amount_used, unit, inventory_item['unit'])
                        if converted is not None:
                            Inventory.update_quantity(user_id, ingredient_name, -converted)
        
        return True
*******
{% extends "base.html" %}

{% block title %}CookBookIt - Profile{% endblock %}

{% block content %}
<div class="slide-in-up">
    <h1 class="mb-4">Your Profile</h1>
    
    <div class="card mb-4">
        <div class="card-body">
            <h2 class="card-title">Account Information</h2>
            <p><strong>Username:</strong> {{ current_user.username }}</p>
            <p><strong>Email:</strong> {{ current_user.email }}</p>
            <p><strong>Member since:</strong> {{ member_since.strftime('%B %d, %Y') }}</p>
        </div>
    </div>
    
    <div class="card mb-4">
        <div class="card-body">
            <h2 class="card-title">Dietary Preferences</h2>
            
            <form method="POST" action="{{ url_for('auth.update_preferences') }}">
                <div class="form-group">
                    <div>
                        <input type="checkbox" id="vegetarian" name="vegetarian" class="mr-2"
                              {% if preferences and preferences.is_vegetarian %}checked{% endif %}>
                        <label for="vegetarian">Vegetarian</label>
                    </div>
                    <div>
                        <input type="checkbox" id="vegan" name="vegan" class="mr-2"
                              {% if preferences and preferences.is_vegan %}checked{% endif %}>
                        <label for="vegan">Vegan</label>
                    </div>
                    <div>
                        <input type="checkbox" id="gluten_free" name="gluten_free" class="mr-2"
                              {% if preferences and preferences.is_gluten_free %}checked{% endif %}>
                        <label for="gluten_free">Gluten Free</label>
                    </div>
                    <div>
                        <input type="checkbox" id="dairy_free" name="dairy_free" class="mr-2"
                              {% if preferences and preferences.is_dairy_free %}checked{% endif %}>
                        <label for="dairy_free">Dairy Free</label>
                    </div>
                </div>
                
                <button type="submit" class="btn btn-primary mt-3">Update Preferences</button>
            </form>
        </div>
    </div>
    
    <div class="card">
        <div class="card-body">
            <h2 class="card-title">Account Settings</h2>
            
            <div class="mt-3">
                <a href="{{ url_for('auth.change_password') }}" class="btn btn-outline">Change Password</a>
                <a href="{{ url_for('auth.delete_account') }}" class="btn btn-danger" onclick="return confirm('Are you sure you want to delete your account? This cannot be undone.')">Delete Account</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
*********
{% extends "base.html" %}

{% block title %}CookBookIt - Change Password{% endblock %}

{% block content %}
<div class="slide-in-up">
    <h1 class="mb-4">Change Password</h1>
    
    <div class="card">
        <div class="card-body">
            <form method="POST" action="{{ url_for('auth.change_password') }}">
                {{ form.hidden_tag() }}
                
                <div class="form-group">
                    {{ form.current_password.label(class="form-label") }}
                    {{ form.current_password(class="form-control") }}
                    {% if form.current_password.errors %}
                        {% for error in form.current_password.errors %}
                            <span class="text-danger">{{ error }}</span>
                        {% endfor %}
                    {% endif %}
                </div>
                
                <div class="form-group">
                    {{ form.new_password.label(class="form-label") }}
                    {{ form.new_password(class="form-control") }}
                    {% if form.new_password.errors %}
                        {% for error in form.new_password.errors %}
                            <span class="text-danger">{{ error }}</span>
                        {% endfor %}
                    {% endif %}
                </div>
                
                <div class="form-group">
                    {{ form.confirm_password.label(class="form-label") }}
                    {{ form.confirm_password(class="form-control") }}
                    {% if form.confirm_password.errors %}
                        {% for error in form.confirm_password.errors %}
                            <span class="text-danger">{{ error }}</span>
                        {% endfor %}
                    {% endif %}
                </div>
                
                <div class="d-flex justify-content-between mt-4">
                    <a href="{{ url_for('auth.profile') }}" class="btn btn-outline">Cancel</a>
                    <button type="submit" class="btn btn-primary">Update Password</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
**********
{% extends "base.html" %}

{% block title %}CookBookIt - Add Ingredient{% endblock %}

{% block content %}
<div class="slide-in-up">
    <h1 class="mb-4">{{ title }}</h1>
    
    <div class="card">
        <div class="card-body">
            <form method="POST">
                {{ form.hidden_tag() }}
                
                <div class="form-group" style="position: relative;">
                    {{ form.ingredient_name.label(class="form-label") }}
                    {{ form.ingredient_name(class="form-control", id="ingredient-name-input", autocomplete="off") }}
                    <div id="ingredient-suggestions" class="ingredient-suggestions"></div>
                    {% if form.ingredient_name.errors %}
                        {% for error in form.ingredient_name.errors %}
                            <span class="text-danger">{{ error }}</span>
                        {% endfor %}
                    {% endif %}
                </div>
                
                <div class="form-group">
                    {{ form.category.label(class="form-label") }}
                    {{ form.category(class="form-select") }}
                    {% if form.category.errors %}
                        {% for error in form.category.errors %}
                            <span class="text-danger">{{ error }}</span>
                        {% endfor %}
                    {% endif %}
                </div>
                
                <div class="d-flex gap-3">
                    <div class="form-group" style="flex: 1;">
                        {{ form.quantity.label(class="form-label") }}
                        {{ form.quantity(class="form-control", min="0.01", step="0.01") }}
                        {% if form.quantity.errors %}
                            {% for error in form.quantity.errors %}
                                <span class="text-danger">{{ error }}</span>
                            {% endfor %}
                        {% endif %}
                    </div>
                    
                    <div class="form-group" style="flex: 1;">
                        {{ form.unit.label(class="form-label") }}
                        {{ form.unit(class="form-select", id="unit-select") }}
                        {% if form.unit.errors %}
                            {% for error in form.unit.errors %}
                                <span class="text-danger">{{ error }}</span>
                            {% endfor %}
                        {% endif %}
                    </div>
                </div>
                
                <div class="form-group">
                    {{ form.expiry_date.label(class="form-label") }}
                    {{ form.expiry_date(class="form-control", type="date") }}
                    {% if form.expiry_date.errors %}
                        {% for error in form.expiry_date.errors %}
                            <span class="text-danger">{{ error }}</span>
                        {% endfor %}
                    {% endif %}
                </div>
                
                <div class="d-flex justify-content-between mt-4">
                    <a href="{{ url_for('inventory.index') }}" class="btn btn-outline">Cancel</a>
                    <button type="submit" class="btn btn-primary">Save Ingredient</button>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    const ingredientInput = document.getElementById('ingredient-name-input');
    const suggestionsContainer = document.getElementById('ingredient-suggestions');
    const unitSelect = document.getElementById('unit-select');
    
    // Store the ingredient data
    let ingredientData = [];
    
    // Fetch ingredients
    async function fetchIngredients(searchTerm) {
        try {
            const response = await fetch(`/inventory/api/ingredients?term=${searchTerm}`);
            const data = await response.json();
            return data.ingredients;
        } catch (error) {
            console.error('Error fetching ingredients:', error);
            return [];
        }
    }
    
    // Debounce function to prevent too many API calls
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }
    
    // Handle input changes
    const handleInputChange = debounce(async function() {
        const searchTerm = ingredientInput.value.trim().toLowerCase();
        
        if (searchTerm.length < 2) {
            suggestionsContainer.innerHTML = '';
            suggestionsContainer.style.display = 'none';
            return;
        }
        
        // Fetch ingredients that match the search term
        ingredientData = await fetchIngredients(searchTerm);
        
        // Display suggestions
        if (ingredientData.length > 0) {
            suggestionsContainer.innerHTML = '';
            
            ingredientData.forEach(ingredient => {
                const div = document.createElement('div');
                div.className = 'suggestion-item';
                div.textContent = ingredient.name;
                div.addEventListener('click', () => selectIngredient(ingredient));
                suggestionsContainer.appendChild(div);
            });
            
            suggestionsContainer.style.display = 'block';
        } else {
            suggestionsContainer.innerHTML = '';
            suggestionsContainer.style.display = 'none';
        }
    }, 300);
    
    // Select an ingredient from suggestions
    function selectIngredient(ingredient) {
        ingredientInput.value = ingredient.name;
        
        // Set the unit if available
        if (ingredient.unit) {
            // Find the option with this unit value
            for (let i = 0; i < unitSelect.options.length; i++) {
                if (unitSelect.options[i].value === ingredient.unit) {
                    unitSelect.selectedIndex = i;
                    break;
                }
            }
        }
        
        // Hide suggestions
        suggestionsContainer.innerHTML = '';
        suggestionsContainer.style.display = 'none';
    }
    
    // Add event listeners
    ingredientInput.addEventListener('input', handleInputChange);
    
    // Close suggestions when clicking outside
    document.addEventListener('click', function(event) {
        if (event.target !== ingredientInput && event.target !== suggestionsContainer) {
            suggestionsContainer.style.display = 'none';
        }
    });
});
</script>

<style>
.ingredient-suggestions {
    position: absolute;
    z-index: 10;
    background: white;
    border: 1px solid #ced4da;
    border-radius: 0.375rem;
    width: 100%;
    max-height: 200px;
    overflow-y: auto;
    display: none;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.suggestion-item {
    padding: 8px 12px;
    cursor: pointer;
}

.suggestion-item:hover {
    background-color: var(--gray-200);
}
</style>
{% endblock %}
*********
{% extends "base.html" %}

{% block title %}CookBookIt - Recipe Search{% endblock %}

{% block content %}
<div class="slide-in-up">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>Recipe Search</h1>
    </div>
    
    <div class="card mb-4">
        <div class="card-body">
            <form action="{{ url_for('recipe.search') }}" method="GET" class="d-flex gap-2">
                <input type="text" name="term" value="{{ search_term }}" class="form-control" placeholder="Search for recipes...">
                <button type="submit" class="btn btn-primary">Search</button>
                <button type="button" id="filter-toggle" class="btn btn-outline">Show Filters</button>
            </form>
            
            <div id="filter-form" class="mt-3 {% if not (request.args.get('vegetarian') or request.args.get('vegan') or request.args.get('gluten_free') or request.args.get('dairy_free') or request.args.get('max_time') or request.args.get('difficulty')) %}d-none{% endif %}">
                <form action="{{ url_for('recipe.search') }}" method="GET">
                    {% if search_term %}
                        <input type="hidden" name="term" value="{{ search_term }}">
                    {% endif %}
                    
                    <h3 class="mb-2">Filters</h3>
                    
                    <!-- Dietary Preferences -->
                    <div class="mb-3">
                        <h4 class="mb-2">Dietary Preferences</h4>
                        <div class="d-flex flex-wrap gap-3">
                            <div>
                                <input type="checkbox" id="vegetarian" name="vegetarian" {% if request.args.get('vegetarian') == 'on' %}checked{% endif %}>
                                <label for="vegetarian">Vegetarian</label>
                            </div>
                            <div>
                                <input type="checkbox" id="vegan" name="vegan" {% if request.args.get('vegan') == 'on' %}checked{% endif %}>
                                <label for="vegan">Vegan</label>
                            </div>
                            <div>
                                <input type="checkbox" id="gluten_free" name="gluten_free" {% if request.args.get('gluten_free') == 'on' %}checked{% endif %}>
                                <label for="gluten_free">Gluten Free</label>
                            </div>
                            <div>
                                <input type="checkbox" id="dairy_free" name="dairy_free" {% if request.args.get('dairy_free') == 'on' %}checked{% endif %}>
                                <label for="dairy_free">Dairy Free</label>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Time Filter -->
                    <div class="mb-3">
                        <h4 class="mb-2">Maximum Time</h4>
                        <select name="max_time" class="form-select" style="max-width: 200px;">
                            <option value="">Any Time</option>
                            <option value="15" {% if request.args.get('max_time') == '15' %}selected{% endif %}>15 minutes or less</option>
                            <option value="30" {% if request.args.get('max_time') == '30' %}selected{% endif %}>30 minutes or less</option>
                            <option value="45" {% if request.args.get('max_time') == '45' %}selected{% endif %}>45 minutes or less</option>
                            <option value="60" {% if request.args.get('max_time') == '60' %}selected{% endif %}>1 hour or less</option>
                            <option value="90" {% if request.args.get('max_time') == '90' %}selected{% endif %}>1.5 hours or less</option>
                            <option value="120" {% if request.args.get('max_time') == '120' %}selected{% endif %}>2 hours or less</option>
                        </select>
                    </div>
                    
                    <!-- Difficulty Filter -->
                    <div class="mb-3">
                        <h4 class="mb-2">Difficulty</h4>
                        <select name="difficulty" class="form-select" style="max-width: 200px;">
                            <option value="">Any Difficulty</option>
                            <option value="Easy" {% if request.args.get('difficulty') == 'Easy' %}selected{% endif %}>Easy</option>
                            <option value="Medium" {% if request.args.get('difficulty') == 'Medium' %}selected{% endif %}>Medium</option>
                            <option value="Hard" {% if request.args.get('difficulty') == 'Hard' %}selected{% endif %}>Hard</option>
                        </select>
                    </div>
                    
                    <button type="submit" class="btn btn-primary mt-2">Apply Filters</button>
                    <a href="{{ url_for('recipe.search') }}" class="btn btn-outline mt-2 ml-2">Clear Filters</a>
                </form>
            </div>
        </div>
    </div>
    
    <div id="recipe-results" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem;">
        {% if recipes|length > 0 %}
            {% for recipe in recipes %}
                <div class="recipe-card card">
                    <img src="{{ url_for('static', filename=Recipe.get_image_path(recipe._id, recipe.image_url)) }}" alt="{{ recipe.name }}" class="card-img">
                    <div class="card-body">
                        <h3 class="card-title">{{ recipe.name }}</h3>
                        <p class="card-text">{{ recipe.description }}</p>
                        <div class="recipe-meta">
                            <span>{{ recipe.prep_time + recipe.cook_time }} mins</span>
                            <span>{{ recipe.difficulty }}</span>
                        </div>
                        <div class="recipe-tags">
                            {% for tag in recipe.tags[:3] %}
                                <span class="recipe-tag">{{ tag }}</span>
                            {% endfor %}
                            {% for key, value in recipe.dietary_info.items() %}
                                {% if value %}
                                    <span class="recipe-tag badge-info">{{ key|replace('_', ' ')|title }}</span>
                                {% endif %}
                            {% endfor %}
                        </div>
                        <a href="{{ url_for('recipe.detail', recipe_id=recipe._id) }}" class="btn btn-primary mt-2">View Recipe</a>
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <div class="text-center" style="grid-column: 1 / -1;">
                <h3>No recipes found</h3>
                <p>Try a different search term or adjust your filters.</p>
            </div>
        {% endif %}
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    const filterToggle = document.getElementById('filter-toggle');
    const filterForm = document.getElementById('filter-form');
    
    if (filterToggle && filterForm) {
        filterToggle.addEventListener('click', function() {
            if (filterForm.classList.contains('d-none')) {
                filterForm.classList.remove('d-none');
                filterForm.classList.add('slide-in-up');
                filterToggle.textContent = 'Hide Filters';
            } else {
                filterForm.classList.add('d-none');
                filterForm.classList.remove('slide-in-up');
                filterToggle.textContent = 'Show Filters';
            }
        });
        
        // Update button text based on initial state
        if (!filterForm.classList.contains('d-none')) {
            filterToggle.textContent = 'Hide Filters';
        }
    }
});
</script>
{% endblock %}
********
{% extends "base.html" %}

{% block title %}CookBookIt - Meal Plan{% endblock %}

{% block content %}
<div class="slide-in-up">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>Your Meal Plan</h1>
        <div>
            <a href="{{ url_for('meal_plan.grocery_list') }}" class="btn btn-outline">Generate Grocery List</a>
            {% if meal_plans|length > 0 %}
            <a href="{{ url_for('meal_plan.generate_plan', plan_id=meal_plans[0].id) }}" class="btn btn-primary">Auto-Generate Plan</a>
            {% endif %}
        </div>
    </div>
    
    {% if meal_plans|length > 0 %}
        {% set meal_plan = meal_plans[0] %}
        <div class="card mb-4">
            <div class="card-body">
                <h2>Week of {{ meal_plan.week_start_date.strftime('%B %d, %Y') }}</h2>
                
                <div class="meal-plan-grid mt-3">
                    <!-- Headers - days of week -->
                    <div></div>
                    <div class="meal-plan-header">Mon</div>
                    <div class="meal-plan-header">Tue</div>
                    <div class="meal-plan-header">Wed</div>
                    <div class="meal-plan-header">Thu</div>
                    <div class="meal-plan-header">Fri</div>
                    <div class="meal-plan-header">Sat</div>
                    <div class="meal-plan-header">Sun</div>
                    
                    <!-- Breakfast row -->
                    <div class="meal-plan-time">Breakfast</div>
                    {% for day in range(7) %}
                        <div class="meal-plan-cell" data-day="{{ day }}">
                            {% set has_meal = false %}
                            {% for item in meal_plan.items %}
                                {% if item.day_of_week == day and item.meal_type == 'breakfast' %}
                                    {% set has_meal = true %}
                                    <div class="meal-plan-recipe">
                                        <a href="{{ url_for('recipe.detail', recipe_id=item.recipe._id) }}">{{ item.recipe.name }}</a>
                                        <form method="POST" action="{{ url_for('meal_plan.remove_recipe', item_id=item.id) }}" style="display: inline;">
                                            <button type="submit" class="btn btn-sm btn-danger" style="padding: 0.1rem 0.3rem; font-size: 0.7rem;">×</button>
                                        </form>
                                    </div>
                                {% endif %}
                            {% endfor %}
                            
                            {% if not has_meal %}
                                <div class="meal-plan-empty">No meal planned</div>
                                <button class="btn btn-sm btn-outline add-recipe-btn" data-day="{{ day }}" data-meal-type="breakfast">Add</button>
                            {% endif %}
                        </div>
                    {% endfor %}
                    
                    <!-- Lunch row -->
                    <div class="meal-plan-time">Lunch</div>
                    {% for day in range(7) %}
                        <div class="meal-plan-cell" data-day="{{ day }}">
                            {% set has_meal = false %}
                            {% for item in meal_plan.items %}
                                {% if item.day_of_week == day and item.meal_type == 'lunch' %}
                                    {% set has_meal = true %}
                                    <div class="meal-plan-recipe">
                                        <a href="{{ url_for('recipe.detail', recipe_id=item.recipe._id) }}">{{ item.recipe.name }}</a>
                                        <form method="POST" action="{{ url_for('meal_plan.remove_recipe', item_id=item.id) }}" style="display: inline;">
                                            <button type="submit" class="btn btn-sm btn-danger" style="padding: 0.1rem 0.3rem; font-size: 0.7rem;">×</button>
                                        </form>
                                    </div>
                                {% endif %}
                            {% endfor %}
                            
                            {% if not has_meal %}
                                <div class="meal-plan-empty">No meal planned</div>
                                <button class="btn btn-sm btn-outline add-recipe-btn" data-day="{{ day }}" data-meal-type="lunch">Add</button>
                            {% endif %}
                        </div>
                    {% endfor %}
                    
                    <!-- Dinner row -->
                    <div class="meal-plan-time">Dinner</div>
                    {% for day in range(7) %}
                        <div class="meal-plan-cell" data-day="{{ day }}">
                            {% set has_meal = false %}
                            {% for item in meal_plan.items %}
                                {% if item.day_of_week == day and item.meal_type == 'dinner' %}
                                    {% set has_meal = true %}
                                    <div class="meal-plan-recipe">
                                        <a href="{{ url_for('recipe.detail', recipe_id=item.recipe._id) }}">{{ item.recipe.name }}</a>
                                        <form method="POST" action="{{ url_for('meal_plan.remove_recipe', item_id=item.id) }}" style="display: inline;">
                                            <button type="submit" class="btn btn-sm btn-danger" style="padding: 0.1rem 0.3rem; font-size: 0.7rem;">×</button>
                                        </form>
                                    </div>
                                {% endif %}
                            {% endfor %}
                            
                            {% if not has_meal %}
                                <div class="meal-plan-empty">No meal planned</div>
                                <button class="btn btn-sm btn-outline add-recipe-btn" data-day="{{ day }}" data-meal-type="dinner">Add</button>
                            {% endif %}
                        </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    {% else %}
        <div class="alert alert-info">
            <h4>No meal plan found for this week</h4>
            <p>Create a new meal plan to get started.</p>
        </div>
    {% endif %}
    
    {% if recipe_suggestions|length > 0 %}
        <h2 class="mb-3">Suggested Recipes</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem;">
            {% for recipe in recipe_suggestions %}
                <div class="recipe-card card">
                    <img src="{{ url_for('static', filename=Recipe.get_image_path(recipe._id, recipe.image_url)) }}" alt="{{ recipe.name }}" class="card-img">
                    <div class="card-body">
                        <h3 class="card-title">{{ recipe.name }}</h3>
                        <p class="card-text">{{ recipe.description }}</p>
                        <div class="recipe-meta">
                            <span>{{ recipe.prep_time + recipe.cook_time }} mins</span>
                            <span>{{ recipe.difficulty }}</span>
                        </div>
                        <div class="match-indicator">
                            <div class="match-bar" data-percentage="{{ recipe.match_percentage or 0 }}">
                                <div class="match-progress" style="width: 0%"></div>
                            </div>
                            <span class="match-text">{{ recipe.match_percentage|round|int }}%</span>
                        </div>
                        <a href="{{ url_for('recipe.detail', recipe_id=recipe._id) }}" class="btn btn-primary mt-2">View Recipe</a>
                    </div>
                </div>
            {% endfor %}
        </div>
    {% endif %}
    
    <!-- Add Recipe Modal -->
    <div id="meal-plan-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); z-index: 1000; justify-content: center; align-items: center; opacity: 0; transition: opacity 0.3s;">
        <div class="card" style="width: 100%; max-width: 500px; transform: translateY(20px); transition: transform 0.3s;">
            <div class="card-body">
                <h2>Add Recipe to Meal Plan</h2>
                
                <form method="POST" action="{{ url_for('meal_plan.add_recipe') }}">
                    {% if meal_plans|length > 0 %}
                        <input type="hidden" name="plan_id" value="{{ meal_plans[0].id }}">
                    {% endif %}
                    <input type="hidden" id="day_of_week" name="day_of_week" value="0">
                    <input type="hidden" id="meal_type" name="meal_type" value="breakfast">
                    
                    <div class="form-group">
                        <label for="recipe_id" class="form-label">Select Recipe</label>
                        <select id="recipe_id" name="recipe_id" class="form-select">
                            {% for recipe in recipe_suggestions %}
                                <option value="{{ recipe._id }}">{{ recipe.name }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    
                    <div class="d-flex justify-content-between mt-4">
                        <button type="button" id="close-meal-plan-modal" class="btn btn-outline">Cancel</button>
                        <button type="submit" class="btn btn-primary">Add to Meal Plan</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Meal Plan - Add recipe modal
    const addRecipeButtons = document.querySelectorAll('.add-recipe-btn');
    const mealPlanModal = document.getElementById('meal-plan-modal');
    const closeMealPlanModalBtn = document.getElementById('close-meal-plan-modal');
    
    if (addRecipeButtons.length > 0 && mealPlanModal) {
        addRecipeButtons.forEach(button => {
            button.addEventListener('click', function() {
                const day = this.getAttribute('data-day');
                const mealType = this.getAttribute('data-meal-type');
                
                document.getElementById('day_of_week').value = day;
                document.getElementById('meal_type').value = mealType;
                
                mealPlanModal.style.display = 'flex';
                setTimeout(() => {
                    mealPlanModal.classList.add('modal-open');
                }, 10);
            });
        });
        
        if (closeMealPlanModalBtn) {
            closeMealPlanModalBtn.addEventListener('click', function() {
                mealPlanModal.classList.remove('modal-open');
                setTimeout(() => {
                    mealPlanModal.style.display = 'none';
                }, 300);
            });
        }
        
        window.addEventListener('click', function(event) {
            if (event.target === mealPlanModal) {
                mealPlanModal.classList.remove('modal-open');
                setTimeout(() => {
                    mealPlanModal.style.display = 'none';
                }, 300);
            }
        });
    }
    
    // Remove "no meal planned" when adding a recipe (fix for issue #9)
    const recipeForm = document.querySelector('form[action*="add_recipe"]');
    if (recipeForm) {
        recipeForm.addEventListener('submit', function() {
            const day = document.getElementById('day_of_week').value;
            const mealType = document.getElementById('meal_type').value;
            
            // Find the cell that corresponds to this day and meal type
            const cell = document.querySelector(`.meal-plan-cell[data-day="${day}"]`);
            if (cell) {
                const placeholder = cell.querySelector('.meal-plan-empty');
                if (placeholder) {
                    placeholder.style.display = 'none';
                }
            }
        });
    }
    
    // Recipe match percentage visual indicators
    const matchBars = document.querySelectorAll('.match-bar');
    matchBars.forEach(bar => {
        const percentage = parseFloat(bar.getAttribute('data-percentage'));
        const progressBar = bar.querySelector('.match-progress');
        
        setTimeout(() => {
            progressBar.style.width = `${percentage}%`;
            
            // Set color based on match percentage
            if (percentage >= 80) {
                progressBar.style.backgroundColor = 'var(--success)';
            } else if (percentage >= 50) {
                progressBar.style.backgroundColor = 'var(--sage-green)';
            } else if (percentage >= 30) {
                progressBar.style.backgroundColor = 'var(--warning)';
            } else {
                progressBar.style.backgroundColor = 'var(--terracotta)';
            }
        }, 100);
    });
});
</script>

<style>
.meal-plan-grid {
    display: grid;
    grid-template-columns: 100px repeat(7, 1fr);
    gap: 8px;
}

.meal-plan-header, .meal-plan-time {
    font-weight: bold;
    padding: 8px;
    text-align: center;
    background-color: var(--sage-green-light);
    border-radius: 4px;
}

.meal-plan-time {
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: var(--gray-200);
}

.meal-plan-cell {
    padding: 8px;
    min-height: 80px;
    border: 1px solid var(--gray-300);
    border-radius: 4px;
    position: relative;
}

.meal-plan-recipe {
    background-color: var(--sage-green-light);
    padding: 6px;
    border-radius: 4px;
    margin-bottom: 4px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.meal-plan-recipe a {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    flex-grow: 1;
}

.meal-plan-empty {
    color: var(--gray-500);
    font-style: italic;
    margin-bottom: 4px;
}

#meal-plan-modal.modal-open {
    opacity: 1;
}

#meal-plan-modal.modal-open .card {
    transform: translateY(0);
}
</style>
{% endblock %}
********
document.addEventListener('DOMContentLoaded', function() {
  // Handle expiration warnings
  const expirationWarnings = document.querySelectorAll('.expiration-warning');
  if (expirationWarnings.length > 0) {
    setTimeout(() => {
      expirationWarnings.forEach(warning => {
        warning.classList.add('fade-in');
      });
    }, 300);
  }
  
  // Recipe match percentage visual indicators
  const matchBars = document.querySelectorAll('.match-bar');
  matchBars.forEach(bar => {
    const percentage = parseFloat(bar.getAttribute('data-percentage'));
    const progressBar = bar.querySelector('.match-progress');
    
    setTimeout(() => {
      progressBar.style.width = `${percentage}%`;
      
      // Set color based on match percentage
      if (percentage >= 80) {
        progressBar.style.backgroundColor = 'var(--success)';
      } else if (percentage >= 50) {
        progressBar.style.backgroundColor = 'var(--sage-green)';
      } else if (percentage >= 30) {
        progressBar.style.backgroundColor = 'var(--warning)';
      } else {
        progressBar.style.backgroundColor = 'var(--terracotta)';
      }
    }, 100);
  });
  
  // Add ingredient form quantity validations
  const quantityInput = document.getElementById('quantity');
  if (quantityInput) {
    quantityInput.addEventListener('input', function() {
      if (parseFloat(this.value) <= 0) {
        this.setCustomValidity('Quantity must be greater than 0');
      } else {
        this.setCustomValidity('');
      }
    });
  }
  
  // Recipe search filters toggle
  const filterToggle = document.getElementById('filter-toggle');
  const filterForm = document.getElementById('filter-form');
  
  if (filterToggle && filterForm) {
    filterToggle.addEventListener('click', function() {
      if (filterForm.classList.contains('d-none')) {
        filterForm.classList.remove('d-none');
        filterForm.classList.add('slide-in-up');
        filterToggle.textContent = 'Hide Filters';
      } else {
        filterForm.classList.add('d-none');
        filterForm.classList.remove('slide-in-up');
        filterToggle.textContent = 'Show Filters';
      }
    });

    // Update button text based on initial state
    if (!filterForm.classList.contains('d-none')) {
      filterToggle.textContent = 'Hide Filters';
    }
  }
  
  // Recipe detail - Complete recipe modal
  const completeRecipeBtn = document.getElementById('complete-recipe-btn');
  const completeModal = document.getElementById('complete-modal');
  const closeModalBtn = document.getElementById('close-modal');
  
  if (completeRecipeBtn && completeModal) {
    completeRecipeBtn.addEventListener('click', function() {
      completeModal.style.display = 'flex';
      setTimeout(() => {
        completeModal.classList.add('modal-open');
      }, 10);
    });
    
    if (closeModalBtn) {
      closeModalBtn.addEventListener('click', function() {
        completeModal.classList.remove('modal-open');
        setTimeout(() => {
          completeModal.style.display = 'none';
        }, 300);
      });
    }
    
    window.addEventListener('click', function(event) {
      if (event.target === completeModal) {
        completeModal.classList.remove('modal-open');
        setTimeout(() => {
          completeModal.style.display = 'none';
        }, 300);
      }
    });
  }
  
  // Meal Plan - Add recipe modal
  const addRecipeButtons = document.querySelectorAll('.add-recipe-btn');
  const mealPlanModal = document.getElementById('meal-plan-modal');
  const closeMealPlanModalBtn = document.getElementById('close-meal-plan-modal');
  
  if (addRecipeButtons.length > 0 && mealPlanModal) {
    addRecipeButtons.forEach(button => {
      button.addEventListener('click', function() {
        const day = this.getAttribute('data-day');
        const mealType = this.getAttribute('data-meal-type');
        
        document.getElementById('day_of_week').value = day;
        document.getElementById('meal_type').value = mealType;
        
        mealPlanModal.style.display = 'flex';
        setTimeout(() => {
          mealPlanModal.classList.add('modal-open');
        }, 10);
      });
    });
    
    if (closeMealPlanModalBtn) {
      closeMealPlanModalBtn.addEventListener('click', function() {
        mealPlanModal.classList.remove('modal-open');
        setTimeout(() => {
          mealPlanModal.style.display = 'none';
        }, 300);
      });
    }
    
    window.addEventListener('click', function(event) {
      if (event.target === mealPlanModal) {
        mealPlanModal.classList.remove('modal-open');
        setTimeout(() => {
          mealPlanModal.style.display = 'none';
        }, 300);
      }
    });
    
    // Remove "no meal planned" when adding a recipe (fix for issue #9)
    const recipeForm = document.querySelector('form[action*="add_recipe"]');
    if (recipeForm) {
      recipeForm.addEventListener('submit', function() {
        const day = document.getElementById('day_of_week').value;
        const mealType = document.getElementById('meal_type').value;
        
        // Find the cell that corresponds to this day and meal type
        const cell = document.querySelector(`.meal-plan-cell[data-day="${day}"]`);
        if (cell) {
          const placeholder = cell.querySelector('.meal-plan-empty');
          if (placeholder) {
            placeholder.style.display = 'none';
          }
        }
      });
    }
  }
  
  // Category filters for inventory
  const categoryFilters = document.querySelectorAll('.category-filter');
  const inventoryItems = document.querySelectorAll('.inventory-item');
  
  if (categoryFilters.length > 0 && inventoryItems.length > 0) {
    categoryFilters.forEach(filter => {
      filter.addEventListener('click', function() {
        const category = this.getAttribute('data-category');
        
        // Toggle active state
        categoryFilters.forEach(f => f.classList.remove('active'));
        this.classList.add('active');
        
        // Filter items
        if (category === 'all') {
          inventoryItems.forEach(item => {
            item.style.display = 'block';
          });
        } else {
          inventoryItems.forEach(item => {
            if (item.getAttribute('data-category') === category) {
              item.style.display = 'block';
            } else {
              item.style.display = 'none';
            }
          });
        }
      });
    });
  }
  
  // Mobile navigation toggle
  const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
  const mobileMenu = document.getElementById('mobile-menu');
  
  if (mobileMenuToggle && mobileMenu) {
    mobileMenuToggle.addEventListener('click', function() {
      mobileMenu.classList.toggle('show');
      mobileMenuToggle.classList.toggle('open');
    });
  }

  // Ingredient autocomplete - Initialize if on inventory add/edit page
  const ingredientInput = document.getElementById('ingredient-name-input');
  const suggestionsContainer = document.getElementById('ingredient-suggestions');
  const unitSelect = document.getElementById('unit-select');
  
  if (ingredientInput && suggestionsContainer && unitSelect) {
    // Store the ingredient data
    let ingredientData = [];
    
    // Fetch ingredients
    async function fetchIngredients(searchTerm) {
      try {
        const response = await fetch(`/inventory/api/ingredients?term=${searchTerm}`);
        const data = await response.json();
        return data.ingredients;
      } catch (error) {
        console.error('Error fetching ingredients:', error);
        return [];
      }
    }
    
    // Debounce function to prevent too many API calls
    function debounce(func, wait) {
      let timeout;
      return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
      };
    }
    
    // Handle input changes
    const handleInputChange = debounce(async function() {
      const searchTerm = ingredientInput.value.trim().toLowerCase();
      
      if (searchTerm.length < 2) {
        suggestionsContainer.innerHTML = '';
        suggestionsContainer.style.display = 'none';
        return;
      }
      
      // Fetch ingredients that match the search term
      ingredientData = await fetchIngredients(searchTerm);
      
      // Display suggestions
      if (ingredientData.length > 0) {
        suggestionsContainer.innerHTML = '';
        
        ingredientData.forEach(ingredient => {
          const div = document.createElement('div');
          div.className = 'suggestion-item';
          div.textContent = ingredient.name;
          div.addEventListener('click', () => selectIngredient(ingredient));
          suggestionsContainer.appendChild(div);
        });
        
        suggestionsContainer.style.display = 'block';
      } else {
        suggestionsContainer.innerHTML = '';
        suggestionsContainer.style.display = 'none';
      }
    }, 300);
    
    // Select an ingredient from suggestions
    function selectIngredient(ingredient) {
      ingredientInput.value = ingredient.name;
      
      // Set the unit if available
      if (ingredient.unit) {
        // Find the option with this unit value
        for (let i = 0; i < unitSelect.options.length; i++) {
          if (unitSelect.options[i].value === ingredient.unit) {
            unitSelect.selectedIndex = i;
            break;
          }
        }
      }
      
      // Hide suggestions
      suggestionsContainer.innerHTML = '';
      suggestionsContainer.style.display = 'none';
    }
    
    // Add event listeners
    ingredientInput.addEventListener('input', handleInputChange);
    
    // Close suggestions when clicking outside
    document.addEventListener('click', function(event) {
      if (event.target !== ingredientInput && event.target !== suggestionsContainer) {
        suggestionsContainer.style.display = 'none';
      }
    });
  }
});

// Function to update recipe search results dynamically
function updateRecipeResults(recipes) {
  const resultsContainer = document.getElementById('recipe-results');
  
  if (!resultsContainer || !recipes) return;
  
  let html = '';
  
  if (recipes.length === 0) {
    html = '<p class="text-center">No recipes found matching your criteria.</p>';
  } else {
    recipes.forEach(recipe => {
      html += `
        <div class="recipe-card card">
          <img src="/static/images/recipes/${recipe._id}.jpg" onerror="this.src='/static/images/placeholder.jpg'" alt="${recipe.name}" class="card-img">
          <div class="card-body">
            <h3 class="card-title">${recipe.name}</h3>
            <p class="card-text">${recipe.description}</p>
            <div class="recipe-meta">
              <span>${recipe.prep_time + recipe.cook_time} mins</span>
              <span>${recipe.difficulty}</span>
            </div>
            <div class="match-indicator">
              <div class="match-bar" data-percentage="${recipe.match_percentage || 0}">
                <div class="match-progress" style="width: 0%"></div>
              </div>
              <span class="match-text">${Math.round(recipe.match_percentage || 0)}%</span>
            </div>
            <div class="recipe-tags">
              ${recipe.tags.map(tag => `<span class="recipe-tag">${tag}</span>`).join('')}
            </div>
            <a href="/recipe/${recipe._id}" class="btn btn-primary mt-2">View Recipe</a>
          </div>
        </div>
      `;
    });
  }
  
  resultsContainer.innerHTML = html;
  
  // Initialize match bars after updating content
  const matchBars = document.querySelectorAll('.match-bar');
  matchBars.forEach(bar => {
    const percentage = parseFloat(bar.getAttribute('data-percentage'));
    const progressBar = bar.querySelector('.match-progress');
    
    setTimeout(() => {
      progressBar.style.width = `${percentage}%`;
      
      // Set color based on match percentage
      if (percentage >= 80) {
        progressBar.style.backgroundColor = 'var(--success)';
      } else if (percentage >= 50) {
        progressBar.style.backgroundColor = 'var(--sage-green)';
      } else if (percentage >= 30) {
        progressBar.style.backgroundColor = 'var(--warning)';
      } else {
        progressBar.style.backgroundColor = 'var(--terracotta)';
      }
    }, 100);
  });
}
