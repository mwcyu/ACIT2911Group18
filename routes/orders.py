from flask import Flask, render_template, redirect, url_for, jsonify, Blueprint, request
from models import Customer,Category,Product,Order,ProductOrder
from pathlib import Path
from db import db
from datetime import datetime as dt

import operator


orders_bp = Blueprint("orders", __name__)

@orders_bp.route("/")
def orders_page():
    sort = request.args.get("sort", "id")
    sort_order = request.args.get("sort_order", "asc")
    date_filter = request.args.get("date_filter")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if start_date and start_date != "None":
        start_date_obj = dt.strptime(start_date, "%Y-%m-%d")
    if end_date and end_date != "None":
        end_date_obj = dt.strptime(end_date, "%Y-%m-%d")


    stmt = db.select(Order)
    
    if start_date != "None" and end_date != "None" and date_filter and start_date and end_date:
        if date_filter == "completed_filter":
            stmt = stmt.where(Order.completed >= start_date_obj).where(Order.completed <= end_date_obj)
            # stmt = stmt.where(Order.completed.between(start_date_obj,end_date_obj))
        else:
            stmt = stmt.where(Order.created >= start_date_obj, Order.created <= end_date_obj).where(Order.completed == None)
            # stmt = stmt.where(Order.created.between(start_date_obj,end_date_obj)).where(Order.completed == None)
    
    sort_options ={
        "id": Order.id,
        "created": Order.created,
        "completed": Order.completed,
        "amount": Order.amount
    }

    if sort in sort_options:
        if sort_order == "desc":
            stmt = stmt.order_by(sort_options[sort].desc())
        if sort_order == "asc":
            stmt = stmt.order_by(sort_options[sort].asc())
    
    orders = db.session.execute(stmt).scalars()
    
    
    if sort == "customer":
        # orders = [order.to_json() for order in orders]
        if sort_order == "asc":
            orders = sorted(orders, key=lambda o:o.customer.name)
            # orders = sorted(orders, key=operator.attrgetter("customer.name"))
        else:
            orders = sorted(orders, key=lambda o:o.customer.name, reverse= True)
            # orders = sorted(orders, key=operator.attrgetter("customer.name"), reverse= True)
    

    return render_template("orders.html",
        orders=orders,
        sort=sort,
        sort_order=sort_order,
        start_date=start_date,
        end_date=end_date,
        date_filter=date_filter)


@orders_bp.route("/<int:order_id>")
def single_order_page(order_id):

    stmt = db.select(Order).where(Order.id == order_id)
    product_order = db.session.execute(stmt).scalar()


    return render_template("order.html", order=product_order)


@orders_bp.route("/<int:id>/complete", methods=["POST"])
def complete_order(id):
    stmt = db.select(Order).where(Order.id == id)
    order = db.session.execute(stmt).scalar()

    try:
        order.complete()
        db.session.add(order)
        db.session.commit()
        return redirect(url_for("orders.single_order_page", order_id=id))
    except ValueError as e:
        return render_template("error.html", message=f"{str(e)}"), 409
    