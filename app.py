import os
from pathlib import Path
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_required, current_user
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

from db import db
from models import Customer, Category, Product, Coupon, Season
from routes.cart import get_applied_coupon

# Load environment variables
load_dotenv()

mail = Mail()
login_manager = LoginManager()
login_manager.login_view = "auth.login"

oauth = OAuth()
github = None  # will initialize later with app context

def create_app(config_override=None):
    app = Flask(__name__)
    app.instance_path = Path(".").resolve()

    # Base config
    app.secret_key = os.getenv("SECRET_KEY", "fallback-secret")
    app.config.from_object("config.Config")

    # Optional override (for testing)
    if config_override:
        app.config.update(config_override)

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    oauth.init_app(app)

    global github
    github = oauth.register(
        name="github",
        client_id=os.getenv("GITHUB_CLIENT_ID"),
        client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
        access_token_url="https://github.com/login/oauth/access_token",
        authorize_url="https://github.com/login/oauth/authorize",
        api_base_url="https://api.github.com/",
        client_kwargs={"scope": "user:email"},
    )
    app.config["GITHUB_OAUTH_CLIENT"] = github

    @login_manager.user_loader
    def load_user(user_id):
        stmt = db.select(Customer).where(Customer.id == user_id)
        return db.session.execute(stmt).scalar_one_or_none()

    # Register blueprints
    from routes import register_blueprints
    register_blueprints(app)

    def get_coupon_progress(user):
        """Calculate coupon progress for the user's active cart."""
        if not user.is_authenticated or not user.active_cart_id:
            return None
        
        active_cart = next((o for o in user.orders if o.id == user.active_cart_id), None)
        if not active_cart:
            return None
        
        applied_coupon = get_applied_coupon(user)
        if not applied_coupon or not applied_coupon.minimum_purchase:
            return None
        
        total = active_cart.estimate()
        progress = round((total / applied_coupon.minimum_purchase * 100))
        remaining = max(0, applied_coupon.minimum_purchase - total)
        
        return {
            'coupon': applied_coupon,
            'total': total,
            'progress': progress,
            'remaining': remaining,
            'is_complete': progress >= 100
        }

    # --- Core Routes ---
    @app.route("/")
    @login_required
    def home_page():
        categories = db.session.execute(db.select(Category)).scalars()
        products = db.session.execute(db.select(Product).where(Product.in_season == True)).scalars()
        active_season = db.session.execute(db.select(Season).where(Season.active == True)).scalar_one_or_none()
        
        # Get coupon progress data
        coupon_progress = get_coupon_progress(current_user)
        
        if active_season:
            return redirect(url_for(f"{active_season.name.lower()}_page"))
        return render_template("home.html", 
                             categories=categories, 
                             products=products,
                             coupon_progress=coupon_progress)

    @app.route("/<season>")
    def seasonal_page(season):
        categories = db.session.execute(db.select(Category)).scalars()
        products = db.session.execute(db.select(Product).where(Product.season_name == season)).scalars()
        coupon_progress = get_coupon_progress(current_user)
        return render_template(f"{season}.html", 
                             categories=categories, 
                             products=products,
                             coupon_progress=coupon_progress)

    @app.route("/dashboard")
    @login_required
    def dashboard_page():
        return render_template("dashboard.html", orders=current_user.orders, coupons=current_user.coupons)

    @app.route("/spin-wheel", methods=["GET", "POST"])
    @login_required
    def spin_wheel():
        if request.method == "POST":
            code = request.form.get("coupon_code")
            if code and code != "NO_PRIZE":
                coupon = db.session.execute(
                    db.select(Coupon).where(Coupon.code == code, Coupon.active == True)
                ).scalar_one_or_none()
                if not coupon:
                    flash("Invalid coupon code.", "danger")
                elif coupon in current_user.coupons:
                    flash("You already have this coupon!", "info")
                else:
                    current_user.coupons.append(coupon)
                    db.session.commit()
                    flash(f"{coupon.code} added to your account!", "success")
                    return redirect(url_for("dashboard_page"))
            return redirect(url_for("spin_wheel"))

        coupons = db.session.execute(db.select(Coupon).where(Coupon.active == True)).scalars().all()
        wheel_data = [{
            "code": c.code,
            "description": c.description,
            "discount_amount": float(c.discount_amount),
            "is_percent": c.is_percent,
            "minimum_purchase": float(c.minimum_purchase) if c.minimum_purchase else None
        } for c in coupons]

        return render_template("spin_wheel.html", wheel_coupons=wheel_data)

    @app.route("/apply-coupon", methods=["POST"])
    @login_required
    def apply_coupon():
        code = request.form.get("coupon_code")
        flash(f"Coupon {code} applied!", "success")
        return redirect(url_for("cart.generate_cart"))

        # Game routes moved to routes/game.py
    
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

    return app

# Local dev run
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=8888)
