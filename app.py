import os
from pathlib import Path
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_required, current_user
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

from db import db
from models import Customer, Category, Product, Coupon, Season

# Load .env variables
load_dotenv()

# --- Flask App Config ---
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret')
app.config.from_object("config.Config")
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
@login_required
def home_page():
    categories = db.session.execute(db.select(Category)).scalars()
    products = db.session.execute(db.select(Product).where(Product.in_season == True)).scalars()
    active_season = db.session.execute(db.select(Season).where(Season.active == True)).scalar_one_or_none()
        
    if active_season:
        return redirect(url_for(f"{active_season.name.lower()}_page"))

    return render_template("home.html", categories=categories, current_user=current_user, products=products)

@app.route("/spring")
def spring_page():
    categories = db.session.execute(db.select(Category)).scalars()
    products = db.session.execute(db.select(Product).where(Product.season_name == "spring")).scalars()
    return render_template("spring.html", categories=categories, current_user=current_user, products=products)

@app.route("/summer")
def summer_page():
    categories = db.session.execute(db.select(Category)).scalars()
    products = db.session.execute(db.select(Product).where(Product.season_name == "summer")).scalars()
    return render_template("summer.html", categories=categories, current_user=current_user, products=products)

@app.route("/fall")
def fall_page():
    categories = db.session.execute(db.select(Category)).scalars()
    products = db.session.execute(db.select(Product).where(Product.season_name == "fall")).scalars()
    return render_template("fall.html", categories=categories, current_user=current_user, products=products)

@app.route("/winter")
def winter_page():
    categories = db.session.execute(db.select(Category)).scalars()
    products = db.session.execute(db.select(Product).where(Product.season_name == "winter")).scalars()
    return render_template("winter.html", categories=categories, current_user=current_user, products=products)

@app.route("/dashboard")
@login_required
def dashboard_page():
    # Get user's coupons
    user_coupons = current_user.coupons
    return render_template("dashboard.html", orders=current_user.orders, coupons=user_coupons)

@app.route("/spin-wheel", methods=["GET", "POST"])
@login_required
def spin_wheel():
    from flask import request, redirect, url_for, flash
    if request.method == "POST":
        coupon_code = request.form.get("coupon_code")
        if coupon_code != 'NO_PRIZE':
            coupon = db.session.execute(
                db.select(Coupon).where(Coupon.code == coupon_code, Coupon.active == True)
            ).scalar_one_or_none()
            
            if not coupon:
                flash("Invalid coupon code.", "danger")
            elif coupon in current_user.coupons:
                flash("You already have this coupon!", "info")
            else:
                current_user.coupons.append(coupon)
                db.session.commit()
                flash(f"Congratulations! {coupon.code} coupon has been added to your account!", "success")
                return redirect(url_for("dashboard_page"))
        
        return redirect(url_for("spin_wheel"))

    # Get all active coupons for the wheel
    wheel_coupons = db.session.execute(
        db.select(Coupon)
        .where(Coupon.active == True)
    ).scalars().all()
    
    # Convert coupons to dict for JSON serialization
    wheel_coupons = [{
        'code': c.code,
        'description': c.description,
        'discount_amount': float(c.discount_amount),
        'is_percent': c.is_percent,
        'minimum_purchase': float(c.minimum_purchase) if c.minimum_purchase else None
    } for c in wheel_coupons]

    return render_template("spin_wheel.html", wheel_coupons=wheel_coupons)

@app.route("/apply-coupon", methods=["POST"])
@login_required
def apply_coupon():
    from flask import request, redirect, url_for, flash
    coupon_code = request.form.get("coupon_code")
    # Here you would validate the coupon and attach it to the user's session/cart
    # For now, just flash a message and redirect to cart/checkout
    flash(f"Coupon {coupon_code} applied!", "success")
    # You should implement logic to store the coupon for the user's checkout
    return redirect(url_for("cart.generate_cart"))

@app.route('/game')
def game():
    return render_template('game.html')

if __name__ == "__main__":
    app.run(debug=True, port=8888)
