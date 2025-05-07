from flask import Blueprint, redirect, url_for, request, render_template, flash, abort
from flask_login import login_required, current_user, fresh_login_required
from db import db
from models import Product

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

def admin_required(f):
    """Decorator to check if user is an admin"""
    def decorated_function(*args, **kwargs):
        if not getattr(current_user, "is_admin", False):
            flash("You don't have permission to access this page.", "danger")
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route("/dashboard")
@login_required
@fresh_login_required
@admin_required
def admin_dashboard():
    try:
        products = db.session.execute(
            db.select(Product).order_by(Product.name)
        ).scalars().all()
        return render_template("admin_dashboard.html", products=products)
    except Exception as e:
        flash("Error loading dashboard: " + str(e), "danger")
        return redirect(url_for("home_page"))

@admin_bp.route("/toggle_season/<int:product_id>")
@login_required
@admin_required
def toggle_season(product_id):
    try:
        product = db.session.get(Product, product_id)
        if not product:
            flash("Product not found", "warning")
            return abort(404)

        product.in_season = not product.in_season
        db.session.commit()
        flash(f"Updated seasonal status for {product.name}", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating product: {str(e)}", "danger")
    
    return redirect(url_for("admin.admin_dashboard"))
