from flask import (
    session, redirect, url_for, Blueprint,
    render_template, request, flash, abort
)
from flask_login import login_required, current_user
from models import Product, ProductOrder, Order, Customer
from db import db
import random

cart_bp = Blueprint("cart", __name__)


def get_or_create_pending_order(customer):
    if customer.active_cart_id:
        cart = db.session.get(Order, customer.active_cart_id)
        if cart and cart.completed is None:
            return cart
    
    cart = next((o for o in customer.orders if o.completed is None), None)
    
    if not cart:
        cart = Order(customer=customer)
        db.session.add(cart)
        db.session.flush()
        
    customer.active_cart_id = cart.id
    db.session.commit()
    
    return cart


@cart_bp.route("/add/<int:id>")
@login_required
def add_to_cart(id: int):
    product = db.session.get(Product, id)
    if not product:
        abort(404)

    order = get_or_create_pending_order(current_user)
    item = next((i for i in order.items if i.product_id == id), None)

    if item:
        item.quantity += 1
    else:
        order.items.append(ProductOrder(product_id=id, quantity=1))

    db.session.commit()
    flash(f"Added {product.name} to your cart.", "success")
    return redirect(request.referrer or url_for("dashboard_page"))


@cart_bp.route("/checkout")
@login_required
def checkout_cart():
    order = get_or_create_pending_order(current_user)

    if not order.items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("cart.view_cart"))


    try:
        order.complete()
        db.session.commit()
        session.pop("active_order_id", None)
        flash("Order completed successfully!", "success")
    except ValueError:
        db.session.rollback()
        flash("One or more items exceed available stock.", "danger")

    return redirect(url_for("dashboard_page"))


@cart_bp.route("/")
@login_required
def view_cart():
    order = get_or_create_pending_order(current_user)

    cart_items = []
    
    for item in order.items:
        product = item.product
        cart_items.append({
            "id": product.id,
            "name": product.name,
            "price": float(product.price),
            "quantity": item.quantity,
            "subtotal": round(float(product.price)*item.quantity,2)
        })

    return render_template("cart.html", cart_items=cart_items, total=order.estimate())


@cart_bp.route("/update/<int:product_id>", methods=["POST"])
@login_required
def update_cart_item(product_id: int):
    try:
        quantity = int(request.form.get("quantity", 1))
    except ValueError:
        flash("Invalid quantity.", "danger")
        return redirect(url_for("cart.view_cart"))

    order = get_or_create_pending_order(current_user)
    item = next((i for i in order.items if i.product_id == product_id), None)

    if not item:
        flash("Item not found in cart.", "warning")
        return redirect(url_for("cart.view_cart"))

    if quantity <= 0:
        db.session.delete(item)
        flash("Item removed from cart.", "info")
    else:
        item.quantity = quantity
        flash("Quantity updated.", "success")

    db.session.commit()
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/remove/<int:product_id>")
@login_required
def remove_cart_item(product_id: int):
    order = get_or_create_pending_order(current_user)
    item = next((i for i in order.items if i.product_id == product_id), None)

    if item:
        db.session.delete(item)
        db.session.commit()
        flash("Item removed.", "info")
    else:
        flash("Item not found in cart.", "warning")

    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/generate", methods=["GET", "POST"])
@login_required
def generate_cart():
    if request.method == "POST":
        try:
            budget = float(request.form["budget"])
            if budget <= 0:
                raise ValueError
        except (ValueError, KeyError):
            flash("Please enter a valid positive budget.", "danger")
            return redirect(url_for("cart.generate_cart"))

        stmt = db.select(Product).where(
            Product.seasonal == True,
            Product.in_season == True,
            Product.available > 0
        )
        products = db.session.execute(stmt).scalars().all()
        random.shuffle(products)

        selected_items = []
        total = 0.0

        for product in products:
            max_qty_affordable = int((budget - total) // float(product.price))
            max_qty = min(product.available, max_qty_affordable)

            if max_qty <= 0:
                continue

            quantity = random.randint(1, max_qty)
            subtotal = quantity * float(product.price)
            total += subtotal

            selected_items.append((product, quantity))

        cart = Order(customer=current_user)
        db.session.add(cart)
        db.session.flush()
        
        current_user.active_cart_id = cart.id
        for product, quantity in selected_items:
            db.session.add(ProductOrder(product_id=product.id, order_id=cart.id, quantity=quantity))

        db.session.commit()
        flash("Generated a cart under your budget.", "success")
        return redirect(url_for("cart.view_cart"))

    return render_template("generate_cart.html")


@cart_bp.route("/switch/<int:order_id>")
@login_required
def switch_pending_order(order_id: int):
    order = db.session.get(Order, order_id)

    # Check order validity
    if not order:
        abort(404)
    if order.customer_id != current_user.id or order.completed is not None:
        abort(403)

    # Update customer's active cart
    current_user.active_cart_id = order.id
    db.session.commit()

    flash(f"Switched to order #{order.id}", "info")
    return redirect(request.referrer)

