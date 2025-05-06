from flask import Flask, render_template
from config import Config
from routes.auth_routes import auth_bp
from routes.inventory_routes import inventory_bp
from routes.recipe_routes import recipe_bp
from routes.meal_plan_routes import meal_plan_bp
from database.mongo_setup import init_mongo
from database.mysql_setup import init_mysql, create_tables
from flask_login import LoginManager
from models.user import User

app = Flask(__name__)
app.config.from_object(Config)

# Initialize databases
mongo_db = init_mongo(app)
mysql_db = init_mysql(app)
create_tables()

# Setup login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(recipe_bp)
app.register_blueprint(meal_plan_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)