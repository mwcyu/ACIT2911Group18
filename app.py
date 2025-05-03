from flask import Flask, render_template
from flask_login import LoginManager, login_required, current_user
from flask_mail import Mail
from pathlib import Path

from db import db
from models import Customer, Category
from routes import (
    api_bp, products_bp, customers_bp, categories_bp,
    orders_bp, practice_bp, cart_bp, auth_bp, admin_bp
)

# Initialize Flask app and extensions
app = Flask(__name__)
app.config.from_object("config.Config")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project1.db"
app.instance_path = Path(".").resolve()

mail = Mail(app)
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = "auth.login"  # FIXED: must match the endpoint name
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    stmt = db.select(Customer).where(Customer.id == user_id)
    return db.session.execute(stmt).scalar_one_or_none()

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

# Routes
@app.route("/")
def home_page():
    stmt = db.select(Category)
    categories = db.session.execute(stmt).scalars()
    return render_template("base.html", categories=categories, current_user=current_user)

@app.route("/dashboard")
@login_required
def dashboard_page():
    orders = current_user.orders
    return render_template("dashboard.html", orders=orders)

if __name__ == "__main__":
    app.run(debug=True, port=8888)
