from flask import Flask, render_template, redirect, url_for, jsonify, Blueprint, request
from models import Customer,Category,Product,Order,ProductOrder
from pathlib import Path
from db import db
from datetime import datetime as dt
import operator

api_bp = Blueprint("api", __name__)
from .products_api import products_api_bp
api_bp.register_blueprint(products_api_bp, url_prefix="/products")
# api_bp.register_blueprint

@api_bp.route("/test")
def example_api():
    return jsonify(["a", {"example": True, "other": "yes"}, ("value", "123")])

@api_bp.route("/orders/<id>", methods=["PUT"])
def complete_order_api(id):
    stmt = db.select(Order).where(Order.id == id)
    order = db.session.execute(stmt).scalar()

    if not order:
        return jsonify({"error": "Order doesn't exist"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request is Invalid"}), 404
    
    if order.completed:
        return jsonify([order.to_json()]), 201
    

    if data["strategy"] == "adjust":
        for item in order.items:
            if item.product.available < item.quantity:
                item.quantity = item.product.available
        db.session.commit()
        order.complete()
    elif data["strategy"] == "delete":
        for item in order.items:
            if item.product.available < item.quantity:
                db.session.delete(item)
        db.session.commit()
        order.complete()
    elif data["strategy"] == "ignore":
        ignore = False
        for item in order.items:
            if item.product.available < item.quantity:
                ignore = True # we will ignore this order
        if ignore == False: # if we don't ignore the order, we complete it
            order.complete()   
            
              
    db.session.commit()

    return jsonify([order.to_json()]), 200
    
@api_bp.route("/orders/")
def orders_api():
    sort = request.args.get("sort", "id")
    sort_order = request.args.get("sort_order", "asc")
    date_filter = request.args.get("date_filter")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if start_date and start_date != "None" and start_date != None:
        start_date_obj = dt.strptime(start_date, "%Y-%m-%d")
    if end_date and end_date != "None" and end_date != None:
        end_date_obj = dt.strptime(end_date, "%Y-%m-%d")

    stmt = db.select(Order)
    if start_date != "None" and end_date != "None" and date_filter and start_date and end_date:
        if date_filter == "completed_filter":
            stmt = stmt.where(Order.completed.between(start_date_obj,end_date_obj))
        else:
            stmt = stmt.where(
                Order.created.between(start_date_obj,end_date_obj),
                Order.completed == None)
    
    sort_options ={
        "id": Order.id,
        "created": Order.created,
        "completed": Order.completed,
        "amount": Order.amount
    }

    if sort in sort_options:
            stmt = stmt.order_by(sort_options[sort].desc() if sort_order == "desc" else sort_options[sort].asc())
    
    orders = db.session.execute(stmt).scalars()
    
    if sort == "customer":
        orders = sorted(orders, key=operator.attrgetter("customer.name"), reverse=True if sort_order == "asc" else True)

    return jsonify([order.to_json() for order in orders])


@api_bp.route("/orders", methods=["POST"])
def new_order():
    data = request.get_json()

    if "customer_phone" in data:
        stmt = db.select(Customer).where(Customer.phone == data["customer_phone"])
    if "customer_id" in data:
        stmt = db.select(Customer).where(Customer.id == data["customer_id"])
    customer = db.session.execute(stmt).scalar()
    
    if not customer:
        return {"message": "No customer with that number"}, 400
    
    new_order = Order(customer=customer, created=dt.now())

    db.session.add(new_order)

    for item in data["items"]:
        each_item = db.session.execute(db.select(Product).where(Product.name == item[0])).scalar()
        if not each_item:
            return {"message": "Product doesn't exist"}, 400
        
        quantity = item[1]
        if quantity < 0:
            return {"message": "Not a positive integer"}, 400
        
        # product = db.session.execute(db.select(Product).where(Product.name == data[0])).
        db.session.add(ProductOrder(product=each_item, quantity=quantity,order=new_order))
    
    db.session.commit()

    return jsonify([new_order.to_json()])


@api_bp.route("/orders/<int:id>")
def order_api(id):
    stmt = db.select(Order).where(Order.id == id)
    order = db.session.execute(stmt).scalar()

    try:
        return jsonify(order.to_json())
    except AttributeError as e:
        return {"message": "ID not found"}, 404
    

@api_bp.route("/customers")
def customers_api():
    stmt = db.select(Customer)
    customers = db.session.execute(stmt).scalars()

    return jsonify([customer.to_json() for customer in customers])


@api_bp.route("/categories")
def categories_api():
    stmt = db.select(Category).where(Category.products.any(Product.price > 10))
    categories = db.session.execute(stmt).scalars()

    return jsonify([category.to_json() for category in categories])


@api_bp.route("/categories/<string:name>")
def orders_by_category_api(name):
    stmt = db.select(Order).where(
    Order.items.any(ProductOrder.product.has(Product.category.has(Category.name == name))),
    Order.completed.is_(None)  # Pending orders
)
    orders = db.session.execute(stmt).scalars().all()
    
    if not orders:
        return jsonify({"error": "this category doesn't exist"})
    return jsonify([order.to_json() for order in orders])

@api_bp.route("/recall")
def recall_api():
    stmt = db.select(Customer).where(Customer.orders.any((Order.items.any(ProductOrder.product.has(Product.name == "bread"))).any(Order.completed >= dt(2025,3,20))))

    customers = db.session.execute(stmt).scalars()

    return jsonify([customer.to_json() for customer in customers])


@api_bp.route("/recall2")
def recall2_api():
    stmt = db.select(Customer).where(Customer.orders.any(Order.items.any(ProductOrder.product.has(Product.name == "milk")))).where(Customer.orders.any(Order.completed >= dt(2025,3,20)))

    customers = db.session.execute(stmt).scalars()

    return jsonify([customer.to_json() for customer in customers])


@api_bp.route("/milk")
def milk_api():
    
    stmt = db.select(Customer).where(Customer.orders.any(Order.items.any(ProductOrder.product.has(Product.name == "milk")))).where(Customer.orders.any(Order.completed != None))
    customers = db.session.execute(stmt).scalars()
    
    return jsonify([customer.to_json() for customer in customers])


@api_bp.route("/products/create", methods=["POST"])
def create_product_api():
    data = request.json

    fields = {
        "name": {
            "func": lambda value: type(value) == str and len(value) != 0,
            "required": True,
            "error": "name not good"
            },
        "price": {
            "func": lambda price: price > 0,
            "required": True,
            "error": "price not good"
            },
        "category": {
            "func": lambda value: type(value) == str and len(value) != 0,
            "required": True,
            "error": "category not good"
            },
        "available": {
            "func": lambda v: type(v) == int and v > 0,
            "required": False,
            "error": "available not good"
        }
    }
    # lambda, only do one thing
    # marco = lambda k, v: print(k, "yes", v)
    # d = {"name": "something", "price": 10.99}
    # for thing in ditems():
        # marco(&thing)


    product_input = {}

    for field, value in fields.items():
        if (field not in data):
            if (value["required"]):
                return value["error"], 400
            continue

        elif not value["func"](data[field]):
            return value["error"], 400

        elif field == "category":
            stmt = db.select(Category).where(Category.name == data["category"])
            database_category = db.session.execute(stmt).scalar()

            if database_category:
                product_input["category"] = database_category
            else:
                new_category = Category(name=data["category"])
                db.session.add(new_category)
                db.session.commit()
                product_input["category"] = new_category
        else:
            product_input[field] = data[field]
    new_product = Product(**product_input)
    db.session.add(new_product)
    db.session.commit()
    stmt = db.select(Product)
    all_products = db.session.execute(stmt).scalars()
    
    return jsonify([product.to_json() for product in all_products])


"""
Using datetime with SQLAlchemy
created and completed are now DATETIME columns in SQL, so you will need to provide datetime
objects in Python. For example: order = Order(customer=tim, created=datetime.now()). Another
option is to set the default value of the field. Be careful - do not use datetime.now() as the default value
in your model, otherwise all your objects will have the same timestamp (i.e., the time at which the model was
"loaded").
You can either:
set the default to datetime.now (notice the lack of parentheses)
import SQL functions from SQLAlchemy (accessible from the db object) and use them for the default
value: db.func.now() is the NOW() function in SQL.
"""