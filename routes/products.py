from flask import Flask, render_template, redirect, url_for, jsonify, Blueprint, request
from models import Customer,Category,Product,Order,ProductOrder
from pathlib import Path
from db import db
from datetime import datetime as dt


products_bp = Blueprint("products", __name__)

@products_bp.route("/")
def all_products_page():
    # Get sort parameters
    sort = request.args.get("sort", "id")
    sort_order = request.args.get("sort_order", "asc")
    category_filter = request.args.get("category", "all")
    season_filter = request.args.get("season", "all")
    in_season_filter = request.args.get("in_season", None)

    # Define sort options
    sort_options = {
        "id": Product.id,
        "name": Product.name,
        "price": Product.price,
        "available": Product.available,
        "category": Product.category_id,
        "season": Product.season_name
    }

    # Build the base query
    stmt = db.select(Product)

    # Apply filters
    if category_filter != "all":
        stmt = stmt.where(Product.category.has(Category.name == category_filter))
    if season_filter != "all":
        stmt = stmt.where(Product.season_name == season_filter)
    if in_season_filter:
        stmt = stmt.where(Product.in_season == True)

    # Apply sorting
    if sort in sort_options:
        if sort_order == "asc":
            stmt = stmt.order_by(sort_options[sort].asc())
        else:
            stmt = stmt.order_by(sort_options[sort].desc())

    # Get all categories and seasons for filters
    categories = db.session.execute(db.select(Category).order_by(Category.name)).scalars()
    seasons = db.session.execute(db.select(Product.season_name).distinct()).scalars()
    
    # Execute the query
    products = db.session.execute(stmt).scalars()

    return render_template("products.html",
                         products=products,
                         categories=categories,
                         seasons=seasons,
                         sort_by=sort,
                         sort_order=sort_order,
                         category_filter=category_filter,
                         season_filter=season_filter,
                         in_season_filter=in_season_filter)


@products_bp.route("/<int:id>")
def individual_product_page(id):
    stmt = db.select(Product).where(Product.id == id)
    product = db.session.execute(stmt).scalar_one_or_none()
    return render_template("single_product.html", product=product)