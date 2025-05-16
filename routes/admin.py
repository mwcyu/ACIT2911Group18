from flask import Blueprint, redirect, url_for, request, render_template, flash
from flask_login import login_required, current_user, fresh_login_required
from db import db
from models import Product, Season

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
@login_required
def admin_dashboard():
    if not getattr(current_user, "is_admin", False):
        return "Unauthorized", 403

#hello testing

    products = db.session.execute(db.select(Product).order_by(Product.name)).scalars().all()
    # Get counts for each season
    spring_count = sum(1 for p in products if p.season_name == "spring" and p.in_season)
    summer_count = sum(1 for p in products if p.season_name == "summer" and p.in_season)
    autumn_count = sum(1 for p in products if p.season_name == "fall" and p.in_season)
    winter_count = sum(1 for p in products if p.season_name == "winter" and p.in_season)
    all_season_count = sum(1 for p in products if p.season_name == "all season" and p.in_season)
    
    seasons = db.session.execute(db.select(Season)).scalars().all()

    
    return render_template("admin_dashboard.html", 
                         products=products,
                         spring_count=spring_count,
                         summer_count=summer_count,
                         autumn_count=autumn_count,
                         winter_count=winter_count,
                         all_season_count=all_season_count,
                         seasons=seasons)


@admin_bp.route("/toggle_season/<int:product_id>")
@login_required
def toggle_season(product_id):
    if not getattr(current_user, "is_admin", False):
        return "Unauthorized", 403

    product = db.session.get(Product, product_id)
    if not product:
        return "Product not found", 404

    product.in_season = not product.in_season
    db.session.commit()
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/turn_all_out_of_season")
@login_required
def turn_all_out_of_season():
    if not getattr(current_user, "is_admin", False):
        return "Unauthorized", 403

    products = db.session.execute(db.select(Product)).scalars().all()
    for product in products:
        product.in_season = False
    db.session.commit()

    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/toggle_season_group/<string:season>")
@login_required
def toggle_season_group(season):
    if not getattr(current_user, "is_admin", False):
        return "Unauthorized", 403

    # Get all products for the specified season
    stmt = db.select(Product).where(Product.season_name == season.lower())
    products = db.session.execute(stmt).scalars().all()
    
    # Check if any products are in season to determine the toggle action
    any_in_season = any(p.in_season for p in products)
    
    # Toggle all products of this season
    for product in products:
        product.in_season = not any_in_season
    
    db.session.commit()
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/toggle_active_season/<string:season>")
@login_required
def toggle_active_season(season):
    if not getattr(current_user, "is_admin", False):
        return "Unauthorized", 403

    # Deactivate all seasons
    seasons = db.session.execute(db.select(Season)).scalars().all()
    for s in seasons:
        s.active = False

    # If "default", commit the changes and return
    if season == "default":
        db.session.commit()
        return redirect(url_for("home_page"))

    # Activate the selected season
    selected_season = db.session.scalar(db.select(Season).where(Season.name == season))
    if selected_season:
        selected_season.active = True
        db.session.commit()
    else:
        flash("Season not found.", "danger")

    return redirect(url_for("home_page"))
