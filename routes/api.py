from flask import Flask, render_template, redirect, url_for, jsonify, Blueprint, request
from models import Customer,Category,Product,Order,ProductOrder
from pathlib import Path
from db import db
from datetime import datetime as dt
import operator

api_bp = Blueprint("api", __name__)
# api_bp.register_blueprint


@api_bp.route("/customers/is_admin", methods=["POST"])
def make_admin_api():
    data = request.get_json()

    """
    Expects JSON:
    {
        "toggle_admin_for": 1
    }
    """

    # Validate input
    if not data or "toggle_admin_for" not in data:
        return {"error": "Missing 'toggle_admin_for' in request"}, 400

    stmt = db.select(Customer).where(Customer.id == data["toggle_admin_for"])
    customer = db.session.execute(stmt).scalar_one_or_none()

    if not customer:
        return {"error": "Customer not found"}, 404

    # Toggle admin
    customer.is_admin = not customer.is_admin
    db.session.commit()

    return jsonify(customer.to_json())


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