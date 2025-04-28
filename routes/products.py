from flask import Flask, render_template, redirect, url_for, jsonify, Blueprint, request
from models import Customer,Category,Product,Order,ProductOrder
from pathlib import Path
from db import db
from datetime import datetime as dt


products_bp = Blueprint("products", __name__)

@products_bp.route("/")
def all_products_page():
    sort = request.args.get("sort", "id")
    sort_order = request.args.get("sort_order", "asc")

    sort_options ={
        "id": Product.id,
        "name": Product.name,
        "price": Product.price,
        "available": Product.available
    }
    stmt = db.select(Product)

    if sort_order == "asc":
        stmt = stmt.order_by(sort_options[sort].asc())
    else:
        stmt = stmt.order_by(sort_options[sort].desc())


    products = db.session.execute(stmt).scalars()

    return render_template("products.html",
                           products=products, 
                           sort_by=sort, 
                           sort_order=sort_order)
