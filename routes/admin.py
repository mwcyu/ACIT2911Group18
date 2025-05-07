from flask import Blueprint, redirect, url_for, request, render_template
from flask_login import login_required, current_user, fresh_login_required
from db import db
from models import Product

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
@login_required
@fresh_login_required
def admin_dashboard():
    if not getattr(current_user, "is_admin", False):
        return "Unauthorized", 403

    products = db.session.execute(db.select(Product).order_by(Product.name)).scalars().all()
    return render_template("admin_dashboard.html", products=products)


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
