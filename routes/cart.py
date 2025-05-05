from flask import session, redirect, url_for, Blueprint, render_template, request
from flask_login import login_required, current_user
from models import Product, ProductOrder, Order
from db import db

cart_bp = Blueprint("cart", __name__)

@cart_bp.route("/add/<int:id>")
@login_required
def add_to_cart(id):
    cart = session.get("cart", {})
    
    pid = str(id)
    
    cart[pid] = cart.get(pid, 0) + 1
    
    session["cart"] = cart
    
    return redirect(request.referrer)

@cart_bp.route('/checkout')
@login_required
def checkout_cart():
    cart = session.get("cart", {})

    if not cart:
        return "Your cart is empty."

    # Create a new Order
    new_order = Order(customer=current_user)

    db.session.add(new_order)
    db.session.flush()  # Prepare to use order.id without committing yet

    for pid, qty in cart.items():
        product = db.session.execute(
            db.select(Product).where(Product.id == int(pid))
        ).scalar_one_or_none()

        if product:
            db.session.add(ProductOrder(
                order=new_order,
                product=product,
                quantity=qty
            ))

    db.session.commit()
    session.pop("cart", None)  # Clear cart after checkout

    return redirect(url_for("dashboard_page"))
        

@cart_bp.route("/")
@login_required
def view_cart():
    cart = session.get("cart", {})
    product_ids = [int(pid) for pid in cart.keys()]

    if not product_ids:
        return "Cart is empty"

    stmt = db.select(Product).where(Product.id.in_(product_ids))
    products = db.session.execute(stmt).scalars().all()

    cart_items = []
    total = 0

    for product in products:
        quantity = cart[str(product.id)]
        subtotal = quantity * float(product.price)
        total += subtotal
        cart_items.append({
            "id": product.id,
            "name": product.name,
            "price": float(product.price),
            "quantity": quantity,
            "subtotal": round(subtotal, 2)
        })

    return render_template("cart.html", cart_items=cart_items, total=round(total, 2))

