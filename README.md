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