from flask import Flask, render_template, redirect, url_for, jsonify, Blueprint, request, abort
from models import Customer,Category,Product,Order,ProductOrder
from pathlib import Path
from db import db
from datetime import datetime as dt

categories_bp = Blueprint("categories", __name__)

@categories_bp.route("/")
def categories_page():
    stmt = db.select(Category)
    data = db.session.execute(stmt).scalars()
    stmt2 = db.select(Category)
    data2 = db.session.execute(stmt2).scalars()

    return render_template("categories.html", data = data, categories = data2)


@categories_bp.route("/<string:name>")
def category_detail(name):
    stmt = db.select(Product).where(Product.category.has(Category.name == name)) 
    products = db.session.execute(stmt).scalars()

    stmt2 = db.select(Category).where(Category.name == name)
    data = db.session.execute(stmt2).scalars().first()
    
    if data is None:
        abort(404)


    return render_template("category.html", products = products, category=data)