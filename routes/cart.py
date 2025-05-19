from flask import (
    session, redirect, url_for, Blueprint,
    render_template, request, flash, abort
)
from flask_login import login_required, current_user
from models import Product, ProductOrder, Order, Customer
from models.coupon import Coupon
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


# Helper to get applied coupon from customer

def get_applied_coupon(customer):
    coupon_id = session.get('applied_coupon_id')
    if coupon_id:
        return db.session.get(Coupon, coupon_id)
    return None


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


@cart_bp.route("/apply-coupon", methods=["POST"])
@login_required
def apply_coupon():
    coupon_id = request.form.get("coupon_id")
    if coupon_id == "none":
        session.pop('applied_coupon_id', None)
        flash("Coupon removed.", "info")
        return redirect(url_for("cart.view_cart"))

    coupon = db.session.get(Coupon, coupon_id)
    if not coupon or coupon not in current_user.coupons:
        flash("Invalid or unavailable coupon.", "danger")
        return redirect(url_for("cart.view_cart"))
    
    # Get current cart total
    order = get_or_create_pending_order(current_user)
    cart_total = order.estimate()
    
    # Check minimum purchase requirement
    if coupon.minimum_purchase and cart_total < coupon.minimum_purchase:
        flash(f"This coupon requires a minimum purchase of ${coupon.minimum_purchase:.2f}. Current total: ${cart_total:.2f}", "warning")
        return redirect(url_for("cart.view_cart"))
    
    # If there's already a coupon applied, show that we're replacing it
    current_coupon = get_applied_coupon(current_user)
    if current_coupon:
        flash(f"Replaced coupon {current_coupon.code} with {coupon.code}.", "info")
    
    session['applied_coupon_id'] = coupon.id
    flash(f"Coupon {coupon.code} applied!", "success")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/remove-coupon")
@login_required
def remove_coupon():
    current_coupon = get_applied_coupon(current_user)
    if current_coupon:
        flash(f"Removed coupon {current_coupon.code}.", "info")
        session.pop('applied_coupon_id', None)
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/checkout")
@login_required
def checkout_cart():
    order = get_or_create_pending_order(current_user)
    coupon = get_applied_coupon(current_user)
    if not order.items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("cart.view_cart"))

    total = order.estimate()
    discount = 0
    if coupon:
        if coupon.is_percent:
            discount = total * (coupon.discount_amount / 100)
        else:
            if total >= coupon.minimum_purchase:
                discount = coupon.discount_amount
                
        total = max(0, total - discount)
        flash(f"Coupon {coupon.code} applied: -${discount:.2f}", "success")
        # Remove coupon from customer after use
        current_user.coupons.remove(coupon)
        db.session.commit()
        session.pop('applied_coupon_id', None)

    try:
        order.complete()
        db.session.commit()
        session.pop("active_order_id", None)
        flash(f"Order completed successfully! Total: ${total:.2f}", "success")
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
            "inventory": product.available,
            "subtotal": round(float(product.price)*item.quantity,2)
        })
    # Coupon logic for display
    applied_coupon_id = session.get('applied_coupon_id')
    applied_coupon = None
    discount = 0
    total = order.estimate()
    if applied_coupon_id:
        from models.coupon import Coupon
        applied_coupon = db.session.get(Coupon, applied_coupon_id)
        if applied_coupon:
            if applied_coupon.is_percent:
                discount = total * (applied_coupon.discount_amount / 100)
            else:
                minimum_spent = applied_coupon.minimum_purchase
                discount = applied_coupon.discount_amount
    return render_template(
        "cart.html",
        active_cart=order,
        cart_items=cart_items,
        total=total,
        applied_coupon=applied_coupon,
        discount=discount
    )

@cart_bp.route("/newcart")
@login_required
def new_cart():
    # Get current customer
    customer = db.session.get(Customer, current_user.id)
    
    # Create new cart/order for customer
    new_cart = Order(customer=current_user)
    db.session.add(new_cart)
    db.session.flush()  # Flush to get the new cart ID
    
    # Update customer's active cart ID
    customer.active_cart_id = new_cart.id
    
    # Store cart ID in session
    session["active_order_id"] = new_cart.id
    
    db.session.commit()
    flash("New cart created", "success")
    
    # Redirect back to previous page
    return redirect(request.referrer or url_for("cart.view_cart"))

@cart_bp.route("/removecart/<int:cart_id>")
@login_required
def remove_cart(cart_id):
    cart = db.session.get(Order, cart_id)
    if not cart:
        flash("Cart not found.", "danger")
        return redirect(request.referrer or url_for("cart.view_cart"))

    if cart.customer_id != current_user.id:
        flash("You are not authorized to delete this cart.", "danger")
        return redirect(request.referrer or url_for("cart.view_cart"))

    if cart.completed:
        flash("Can't delete completed orders.", "danger")
        return redirect(request.referrer or url_for("cart.view_cart"))

    # Unset active cart if needed
    if hasattr(current_user, "active_cart_id") and current_user.active_cart_id == cart.id:
        current_user.active_cart_id = None

    db.session.delete(cart)
    db.session.commit()
    flash("Successfully removed cart.", "success")
    return redirect(request.referrer or url_for("cart.view_cart"))

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
    return redirect(request.referrer or url_for("dashboard_page"))

@cart_bp.route("/rename/<int:order_id>", methods=["POST"])
@login_required
def rename_cart(order_id):
    order = db.get_or_404(Order, order_id)
    if order.customer_id != current_user.id or order.completed:
        return "Unauthorized", 403

    new_name = request.form.get("new_name", "").strip()
    if new_name:
        order.name = new_name
        db.session.commit()
        flash("Cart name updated!", "success")
    else:
        flash("Cart name cannot be empty.", "danger")

    return redirect(url_for("cart.view_cart"))
