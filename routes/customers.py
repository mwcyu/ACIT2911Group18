from flask import Flask, render_template, redirect, url_for, jsonify, Blueprint, request
from models import Customer,Category,Product,Order,ProductOrder
from pathlib import Path
from db import db
from datetime import datetime as dt

customers_bp = Blueprint("customers", __name__)

@customers_bp.route("/")
def customers_detail():
    stmt = db.select(Customer)
    data = db.session.execute(stmt).scalars()
    
    return render_template("customers.html", data=data)


@customers_bp.route("/<int:id>")
def customer_detail(id):
    stmt = db.select(Customer).where(Customer.id == id)
    data = db.session.execute(stmt).scalar()
    stmt2 = db.select(Order).where(Order.customer_id == id)
    orders = db.session.execute(stmt2).scalars()
    
    return render_template("customer.html", customer = data, orders=orders)