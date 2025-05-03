# Import necessary modules and extensions
from flask import Flask, render_template  # Flask framework and template rendering
from flask_login import LoginManager, login_required, current_user  # User authentication and session management
from flask_mail import Mail  # Email handling
from pathlib import Path  # File path management

# Import database and models
from db import db  # SQLAlchemy database instance
from models import Customer, Category  # Database models for Customer and Category

# Import blueprints for modular route handling
from routes import (
    api_bp, products_bp, customers_bp, categories_bp,
    orders_bp, practice_bp, cart_bp, auth_bp, admin_bp
)

# Initialize Flask app and configure settings
app = Flask(__name__)
app.config.from_object("config.Config")  # Load configuration from a config class
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project1.db"  # Set SQLite database URI
app.instance_path = Path(".").resolve()  # Set the instance path to the current directory

# Initialize Flask-Mail for email functionality
mail = Mail(app)

# Initialize the database with the Flask app
db.init_app(app)

# Initialize Flask-Login for user authentication
login_manager = LoginManager()
login_manager.login_view = "auth.login"  # Redirect unauthenticated users to the login page
login_manager.init_app(app)  # Attach the login manager to the Flask app

# Define a user loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # Query the database to load the user by their ID
    stmt = db.select(Customer).where(Customer.id == user_id)
    return db.session.execute(stmt).scalar_one_or_none()

# Register blueprints to organize routes into modules
app.register_blueprint(api_bp, url_prefix="/api")  # API routes
app.register_blueprint(products_bp, url_prefix="/products")  # Product-related routes
app.register_blueprint(orders_bp, url_prefix="/orders")  # Order-related routes
app.register_blueprint(categories_bp, url_prefix="/categories")  # Category-related routes
app.register_blueprint(customers_bp, url_prefix="/customers")  # Customer-related routes
app.register_blueprint(practice_bp, url_prefix="/practice")  # Practice-related routes
app.register_blueprint(cart_bp, url_prefix="/cart")  # Shopping cart routes
app.register_blueprint(auth_bp, url_prefix="/auth")  # Authentication routes
app.register_blueprint(admin_bp)  # Admin-related routes (no prefix)

# Define the home page route
@app.route("/")
def home_page():
    # Query all categories from the database
    stmt = db.select(Category)
    categories = db.session.execute(stmt).scalars()
    # Render the base.html template with categories and the current user
    return render_template("base.html", categories=categories, current_user=current_user)

# Define the dashboard page route (requires login)
@app.route("/dashboard")
@login_required
def dashboard_page():
    # Retrieve the current user's orders
    orders = current_user.orders
    # Render the dashboard.html template with the user's orders
    return render_template("dashboard.html", orders=orders)

# Run the application in debug mode on port 8888
if __name__ == "__main__":
    app.run(debug=True,
            port=8888)
