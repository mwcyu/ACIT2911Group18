from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.coupon import Coupon
from db import db

spin_wheel_bp = Blueprint("spin_wheel", __name__)

@spin_wheel_bp.route("/", methods=["GET", "POST"])
@login_required
def spin_wheel():
    if request.method == "POST":
        coupon_code = request.form.get("coupon_code")
        coupon = db.session.execute(db.select(Coupon).where(Coupon.code == coupon_code)).scalar_one_or_none()
        if not coupon:
            flash("Invalid coupon.", "danger")
            return redirect(url_for("spin_wheel.spin_wheel"))
        if coupon not in current_user.coupons:
            current_user.coupons.append(coupon)
            db.session.commit()
            flash(f"Congratulations! Coupon '{coupon.description}' has been added to your account.", "success")
        else:
            flash("You already have this coupon.", "info")
        return redirect(url_for("spin_wheel.spin_wheel"))

    # Only show active coupons for the wheel
    coupons = db.session.execute(db.select(Coupon).where(Coupon.active == True)).scalars().all()
    wheel_coupons = [c.to_json() for c in coupons]
    return render_template("spin_wheel.html", wheel_coupons=wheel_coupons) 