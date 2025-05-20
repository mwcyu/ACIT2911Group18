from flask import Blueprint, redirect, url_for, request, render_template, flash
from flask_login import login_required, current_user, fresh_login_required
from db import db
from models import Product, Season

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/dashboard")
@login_required
def admin_dashboard():
    if not getattr(current_user, "is_admin", False):
        flash("You are not authorized to view this page.", "danger")
        return redirect(url_for("home_page")) # Assuming home_page is a valid route

    products = db.session.execute(db.select(Product).order_by(Product.name)).scalars().all()
    # Get counts for each season
    spring_count = sum(1 for p in products if p.season_name == "spring" and p.in_season)
    summer_count = sum(1 for p in products if p.season_name == "summer" and p.in_season)
    autumn_count = sum(1 for p in products if p.season_name == "fall" and p.in_season)
    winter_count = sum(1 for p in products if p.season_name == "winter" and p.in_season)
    all_season_count = sum(1 for p in products if p.season_name == "all season" and p.in_season)
    
    seasons = db.session.execute(db.select(Season)).scalars().all()
    has_active_season = any(s.active for s in seasons if hasattr(s, 'active'))
    
    return render_template("admin_dashboard.html", 
                         products=products,
                         spring_count=spring_count,
                         summer_count=summer_count,
                         autumn_count=autumn_count,
                         winter_count=winter_count,
                         all_season_count=all_season_count,
                         seasons=seasons,
                         has_active=has_active_season)


@admin_bp.route("/toggle_season/<int:product_id>")
@login_required
def toggle_season(product_id):
    if not getattr(current_user, "is_admin", False):
        flash("You are not authorized to perform this action.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    product = db.session.get(Product, product_id)
    if not product:
        flash(f"Product with ID {product_id} not found.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    product.in_season = not product.in_season
    db.session.commit()
    flash(f"'{product.name}' in_season status has been toggled.", "success")
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/turn_all_out_of_season")
@login_required
def turn_all_out_of_season():
    if not getattr(current_user, "is_admin", False):
        flash("You are not authorized to perform this action.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    products = db.session.execute(db.select(Product)).scalars().all()
    for product in products:
        product.in_season = False
    db.session.commit()
    flash("All products have been set to out of season.", "success")
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/toggle_season_group/<string:season_name>")
@login_required
def toggle_season_group(season_name):
    if not getattr(current_user, "is_admin", False):
        flash("You are not authorized to perform this action.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    stmt = db.select(Product).where(Product.season_name == season_name.lower())
    products_in_group = db.session.execute(stmt).scalars().all()
    
    if not products_in_group:
        flash(f"No products found for season: {season_name.capitalize()}.", "info")
        return redirect(url_for("admin.admin_dashboard"))
    
    any_in_season = any(p.in_season for p in products_in_group)
    new_in_season_state = not any_in_season

    for product in products_in_group:
        product.in_season = new_in_season_state
    db.session.commit()
    
    action = "in season" if new_in_season_state else "out of season"
    flash(f"All products in {season_name.capitalize()} set to {action}.", "success")
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/toggle_active_season/<string:season_name>")
@login_required
def toggle_active_season(season_name):
    if not getattr(current_user, "is_admin", False):
        flash("You are not authorized to perform this action.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    seasons = db.session.execute(db.select(Season)).scalars().all()
    target_season_name_lower = season_name.lower()

    if target_season_name_lower == "default":
        for s in seasons:
            if hasattr(s, 'active'):
                s.active = False
        flash("Homepage theme set to default.", "success")
    else:
        found_target_season = False
        for s in seasons:
            if hasattr(s, 'active'):
                if s.name.lower() == target_season_name_lower:
                    s.active = True
                    found_target_season = True
                else:
                    s.active = False
        
        if found_target_season:
            flash(f"Homepage theme set to {season_name.capitalize()}.", "success")
        else:
            # If the season name is not found, set to default
            for s_fallback in seasons: 
                if hasattr(s_fallback, 'active'):
                    s_fallback.active = False
            flash(f"Season '{season_name.capitalize()}' not found. Theme reset to default.", "warning")

    db.session.commit()
    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/toggle")
@login_required
def admin_toggle():
    pass # Placeholder for potential future use

@admin_bp.route("/update_inventory/<int:product_id>", methods=["POST"])
@login_required
def update_inventory(product_id):
    if not getattr(current_user, "is_admin", False):
        flash("You are not authorized to perform this action.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    product = db.session.get(Product, product_id)
    if not product:
        flash("Product not found.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    try:
        quantity = int(request.form.get("quantity"))
        if quantity < 0:
            flash("Inventory quantity cannot be negative.", "danger")
        else:
            product.available = quantity
            db.session.commit()
            flash(f"{product.name} inventory updated to {quantity}.", "success")
    except ValueError:
        flash("Invalid quantity format.", "danger")
    
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route("/add_inventory_to_all", methods=["POST"])
@login_required
def add_inventory_to_all():
    if not getattr(current_user, "is_admin", False):
        flash("You are not authorized to perform this action.", "danger")
        return redirect(url_for("admin.admin_dashboard"))

    try:
        quantity_to_add = int(request.form.get("quantity_to_add"))
        if quantity_to_add <= 0:
            flash("Quantity to add must be a positive number.", "danger")
        else:
            products = db.session.execute(db.select(Product)).scalars().all()
            for product in products:
                product.available += quantity_to_add
            db.session.commit()
            flash(f"{quantity_to_add} units added to all products' inventory.", "success")
    except ValueError:
        flash("Invalid quantity format.", "danger")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {str(e)}", "danger")
    
    return redirect(url_for("admin.admin_dashboard"))