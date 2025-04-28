from flask import Flask, Blueprint,request,jsonify
from db import db

from models import Product, ProductOrder, Order, Customer, Category

products_api_bp = Blueprint("products_api", __name__)

@products_api_bp.route("/")
def products_api():
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

    return jsonify([product.to_json() for product in products])


@products_api_bp.route("/<int:id>")
def product_api(id):
    stmt = db.select(Product).where(Product.id == id)
    product = db.session.execute(stmt).scalar()
    
    try:
        return jsonify(product.to_json())
    except AttributeError as e:
        return {"message": "ID not found"}, 404


@products_api_bp.route("/<string:name>", methods=["PUT"])
def product_name_api(name):
    stmt = db.select(Product).where(Product.name == name)
    product = db.session.execute(stmt).scalar()
    if not product:
        return jsonify({"error": "Product not found"}), 404 

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    fields = {
        "price": lambda value: isinstance(value, (int,float)) and value > 0,
        "inventory": lambda value: isinstance(value, int) and value >= 0
    }
    
    update = {}
    
    for field, func in fields.items():
        if field in data:
            if not func(data[field]):
                return jsonify({"error": f"Invalid value for {field}"}), 400
            update[field] = data[field]
            
    
    
    if "price" in data:

        product.price = update["price"]

    if "inventory" in data:
        product.available = update["inventory"]

    db.session.commit()
    

    return jsonify(product.to_json()), 200
