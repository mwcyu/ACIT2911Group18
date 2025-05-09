import os
from pathlib import Path
from flask import Flask, render_template
from flask_login import LoginManager, login_required, current_user
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

from db import db
from models import Customer, Category, Product

# Load .env variables
load_dotenv()

# --- Flask App Config ---
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret')
app.config.from_object("config.Config")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project1.db"
app.instance_path = Path(".").resolve()

# --- Extensions ---
db.init_app(app)
mail = Mail(app)

# Flask-Login
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    stmt = db.select(Customer).where(Customer.id == user_id)
    return db.session.execute(stmt).scalar_one_or_none()

# --- Blueprints ---
from routes import (
    api_bp, products_bp, customers_bp, categories_bp,
    orders_bp, practice_bp, cart_bp, auth_bp, admin_bp
)

app.register_blueprint(api_bp, url_prefix="/api")
app.register_blueprint(products_bp, url_prefix="/products")
app.register_blueprint(orders_bp, url_prefix="/orders")
app.register_blueprint(categories_bp, url_prefix="/categories")
app.register_blueprint(customers_bp, url_prefix="/customers")
app.register_blueprint(practice_bp, url_prefix="/practice")
app.register_blueprint(cart_bp, url_prefix="/cart")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(admin_bp)

# --- GitHub OAuth ---
oauth = OAuth(app)
github = oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

app.config['GITHUB_OAUTH_CLIENT'] = github

# --- Routes ---
@app.route("/")
def home_page():
    categories = db.session.execute(db.select(Category)).scalars()
    products = db.session.execute(db.select(Product).where(Product.in_season == True)).scalars()
    return render_template("home.html", categories=categories, current_user=current_user, products=products)

@app.route("/dashboard")
@login_required
def dashboard_page():
    return render_template("dashboard.html", orders=current_user.orders)

if __name__ == "__main__":
    app.run(debug=True, port=8888)
