from flask import Blueprint, jsonify
from db import db
from models import Customer, Product

practice_bp = Blueprint("practice", __name__)

@practice_bp.route("/customer/by-name/<string:name>")
def get_customers_by_name(name):
    stmt = db.select(Customer).where(Customer.name == name)
    
    customers = db.session.execute(stmt).scalars()

    return jsonify([customer.to_json() for customer in customers])


@practice_bp.route("/products_out_of_stock")
def empty_products():
    stmt = db.select(Product).where(Product.available == 0)
    
    products = db.session.execute(stmt).scalars()
    
    print(type(products))
    # print(type(products.all()))
    
    return jsonify([product.to_json() for product in products]),200

# @practice_bp.route("/orders/customer-phone/<string:phone>")
from flask import jsonify, Blueprint, request
from models import Customer,Category,Product,Order,ProductOrder
from db import db
from datetime import datetime as dt

practice = Blueprint("practice", __name__)

@practice.route("/customer/<int:id>/orders")
def customer_orders(id):
    customer = db.session.execute(db.select(Customer).where(Customer.id == id)).scalar()
    return jsonify(customer.to_json())

@practice.route("/products/under_two")
def products_under_two():
    result = db.session.execute(db.select(Product).where(Product.price < 2.0)).scalars()
    return jsonify([product.to_json() for product in result])

@practice.route("/products/empty_stock")
def products_no_stock():
    result = db.session.execute(db.select(Product).where(Product.available == 0)).scalars()
    return jsonify([product.to_json() for product in result])

@practice.route("/customers/match/<string:name>")
def customer_match(name):
    new_name = f"%{name}%"
    result = db.session.execute(db.select(Customer).where(Customer.name.ilike(new_name))).scalars()
    if result:
        return jsonify([customer.to_json() for customer in result])
    else:
        return jsonify({"message":"Customer does not exists"}), 400

@practice.route("/orders/customer_phone/<string:phone>")
def orders_by_phone(phone):
    orders = db.session.execute(db.select(Order).where(Order.customer.has(Customer.phone == phone))).scalars()
    if orders:
        return jsonify([order.to_json() for order in orders])
    else:
        return jsonify({"message":"Order(s) with that customer phone number do not exist"}), 404

@practice.route("/categories/out_of_stock_products")
def all_categories_out_of_stock():
    stmnt = db.session.execute(db.select(Category).where(Category.products.any(Product.available == 0))).scalars().all()
    if not stmnt:
        return jsonify({"message":"No categories have a product out of stock"}), 404
    return jsonify([category.to_json() for category in stmnt]), 200

@practice.route("/products_out_of_stock")
def out_of_stock_products():
    products = db.session.execute(db.select(Product).where(Product.available == 0)).scalars().all()
    if not products:
        return jsonify({"message":"All products are in stock"}), 404
    
    return jsonify([prod.to_json() for prod in products]), 200

@practice.route("/customers/pending_orders")
def customers_pending():
    customers = db.session.execute(db.select(Customer).where(Customer.orders.any(Order.completed == None))).scalars().all()
    if not customers:
        return jsonify({"message":"No customers have pending orders"}), 404
    return jsonify([cus.to_json() for cus in customers]), 400

@practice.route("/customer/<int:id>/orders")
def customer_orders(id):
    customer = db.session.execute(db.select(Customer).where(Customer.id == id)).scalar()
    return jsonify(customer.to_json()), 200

@practice.route("/products/under_two")
def products_under_two():
    result = db.session.execute(db.select(Product).where(Product.price < 2.0)).scalars()
    return jsonify([product.to_json() for product in result]), 200

@practice.route("/products/empty_stock")
def products_no_stock():
    result = db.session.execute(db.select(Product).where(Product.available == 0)).scalars()
    return jsonify([product.to_json() for product in result]), 200

@practice.route("/customers/match/<string:name>")
def customer_match(name):
    new_name = f"%{name}%"
    result = db.session.execute(db.select(Customer).where(Customer.name.ilike(new_name))).scalars()
    if result:
        return jsonify([customer.to_json() for customer in result]), 200
    else:
        return jsonify({"message":"Customer does not exists"}), 400

# @practice.route("/orders/customer_name/<string:name>")
# def orders_by_cus_name(name):
#     new_name = f"%{name}%"
#     orders = db.session.execute(db.select(Order).where(Order.customer.has(Customer.name == new_name))).scalars().all()
#     if not orders:
#         return jsonify({"message":"Customer(s) have no orders"}), 400
#     return jsonify([order.to_json() for order in orders]), 404




# Code      Comment
# 200       OK everything is fine
# 204       OK everything is fine (empty response)
# 400       Bad Request the client did something wrong
# 403       Forbidden Access to this resource is forbidden
# 404       Resource Not Found This resource does not exist
# 405       Method Not Allowed The resource can not be manipulated with that method
# 500       Internal Server Error You should be worried - bug in the application