from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from models.inventory import Inventory
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Optional

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

# Categories for the form dropdown
CATEGORIES = [
    ('vegetable', 'Vegetable'),
    ('fruit', 'Fruit'),
    ('meat', 'Meat'),
    ('dairy', 'Dairy'),
    ('grain', 'Grain'),
    ('spice', 'Spice'),
    ('condiment', 'Condiment'),
    ('bakery', 'Bakery'),
    ('canned goods', 'Canned Goods'),
    ('frozen', 'Frozen'),
    ('beverage', 'Beverage'),
    ('snack', 'Snack'),
    ('other', 'Other')
]

# Units for the form dropdown
UNITS = [
    ('g', 'Grams (g)'),
    ('kg', 'Kilograms (kg)'),
    ('ml', 'Milliliters (ml)'),
    ('l', 'Liters (l)'),
    ('cups', 'Cups'),
    ('tbsp', 'Tablespoons'),
    ('tsp', 'Teaspoons'),
    ('whole', 'Whole'),
    ('slices', 'Slices'),
    ('pieces', 'Pieces'),
    ('pinch', 'Pinch'),
    ('oz', 'Ounces (oz)'),
    ('lb', 'Pounds (lb)'),
    ('cloves', 'Cloves')
]

class InventoryForm(FlaskForm):
    ingredient_name = StringField('Ingredient Name', validators=[DataRequired()])
    category = SelectField('Category', choices=CATEGORIES, validators=[DataRequired()])
    quantity = FloatField('Quantity', validators=[DataRequired()])
    unit = SelectField('Unit', choices=UNITS, validators=[DataRequired()])
    expiry_date = DateField('Expiry Date (Optional)', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Save')

@inventory_bp.route('/')
@login_required
def index():
    inventory_items = Inventory.get_by_user_id(current_user.id)
    expiring_items = Inventory.get_expiring_items(current_user.id)
    return render_template('inventory/index.html', 
                          inventory_items=inventory_items, 
                          expiring_items=expiring_items,
                          categories=CATEGORIES,
                          datetime=datetime)

@inventory_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = InventoryForm()
    
    if form.validate_on_submit():
        item = Inventory.add_item(
            user_id=current_user.id,
            ingredient_name=form.ingredient_name.data.lower(),
            category=form.category.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            expiry_date=form.expiry_date.data
        )
        
        if item:
            flash('Ingredient added to inventory!', 'success')
            return redirect(url_for('inventory.index'))
        else:
            flash('Error adding ingredient. Please try again.', 'danger')
    
    return render_template('inventory/add.html', form=form, title="Add Ingredient")

@inventory_bp.route('/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit(item_id):
    item = Inventory.get_by_id(item_id)
    
    if not item or item.user_id != current_user.id:
        flash('Item not found or you do not have permission to edit it.', 'danger')
        return redirect(url_for('inventory.index'))
    
    form = InventoryForm()
    
    if form.validate_on_submit():
        updated_item = Inventory.update_item(
            item_id=item_id,
            ingredient_name=form.ingredient_name.data.lower(),
            category=form.category.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            expiry_date=form.expiry_date.data
        )
        
        if updated_item:
            flash('Ingredient updated successfully!', 'success')
            return redirect(url_for('inventory.index'))
        else:
            flash('Error updating ingredient. Please try again.', 'danger')
    
    # Pre-fill form
    if request.method == 'GET':
        form.ingredient_name.data = item.ingredient_name
        form.category.data = item.category
        form.quantity.data = item.quantity
        form.unit.data = item.unit
        form.expiry_date.data = item.expiry_date
    
    return render_template('inventory/edit.html', form=form, item=item, title="Edit Ingredient")

@inventory_bp.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def delete(item_id):
    item = Inventory.get_by_id(item_id)
    
    if not item or item.user_id != current_user.id:
        flash('Item not found or you do not have permission to delete it.', 'danger')
        return redirect(url_for('inventory.index'))
    
    if Inventory.delete_item(item_id):
        flash('Ingredient removed from inventory!', 'success')
    else:
        flash('Error removing ingredient. Please try again.', 'danger')
    
    return redirect(url_for('inventory.index'))

@inventory_bp.route('/api/items', methods=['GET'])
@login_required
def api_get_items():
    inventory_items = Inventory.get_by_user_id(current_user.id)
    items_list = []
    
    for item in inventory_items:
        items_list.append({
            'id': item.id,
            'ingredient_name': item.ingredient_name,
            'category': item.category,
            'quantity': item.quantity,
            'unit': item.unit,
            'expiry_date': item.expiry_date.isoformat() if item.expiry_date else None
        })
    
    return jsonify({'items': items_list})