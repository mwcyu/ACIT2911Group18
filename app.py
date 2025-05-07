# Import necessary modules and extensions
from flask import Flask, render_template
from flask_login import login_required, current_user
from flask_mail import Mail
from pathlib import Path
import os

# Import local modules
from db import db
from auth import init_login_manager
from oauth import init_oauth
from forms import init_csrf
from models import Category, Product

# Import blueprints
from routes import (
    api_bp, products_bp, customers_bp, categories_bp,
    orders_bp, practice_bp, cart_bp, auth_bp, admin_bp
)

def create_app(config_class=None):
    # Initialize Flask app
    app = Flask(__name__)
    
    # Load config
    if config_class is None:
        app.config.from_object("config.Config")
    else:
        app.config.from_object(config_class)

    # Initialize core extensions
    db.init_app(app)
    Mail(app)
    init_login_manager(app)
    init_oauth(app)
    init_csrf(app)

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(products_bp, url_prefix="/products")
    app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(categories_bp, url_prefix="/categories")
    app.register_blueprint(customers_bp, url_prefix="/customers")
    app.register_blueprint(practice_bp, url_prefix="/practice")
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp)

    # Context processors
    @app.context_processor
    def inject_categories():
        try:
            stmt = db.select(Category)
            categories = db.session.execute(stmt).scalars()
            return dict(categories=categories)
        except Exception as e:
            app.logger.error(f'Error loading categories: {str(e)}')
            return dict(categories=[])

    # Routes
    @app.route("/")
    def home_page():
        try:
            stmt = db.select(Product).where(Product.in_season == True)
            products = db.session.execute(stmt).scalars()
            return render_template("home.html", current_user=current_user, products=products)
        except Exception as e:
            app.logger.error(f'Error loading home page: {str(e)}')
            return render_template("error.html", message="Error loading products"), 500

    @app.route("/dashboard")
    @login_required
    def dashboard_page():
        try:
            orders = current_user.orders
            return render_template("dashboard.html", orders=orders)
        except Exception as e:
            app.logger.error(f'Error loading dashboard: {str(e)}')
            return render_template("error.html", message="Error loading dashboard"), 500

    return app

# Create the application instance
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=8888)
