from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from models import Coupon
from db import db
import random

# Define available symbols
SYMBOLS = [
    'bi-gift',
    'bi-star',
    'bi-heart',
    'bi-gem',
    'bi-trophy',
    'bi-lightning',
    'bi-award',
    'bi-dice-6',
    'bi-stars'
]

game_bp = Blueprint("game", __name__)

@game_bp.route("/slot-machine", methods=["GET", "POST"])
@login_required
def slot_machine():
    if request.method == "POST":
        # Handle AJAX spin request
        if request.is_json:
            try:
                data = request.get_json()
                if data.get('action') == 'spin':
                    # Get active coupons
                    coupons = db.session.execute(
                        db.select(Coupon).where(Coupon.active == True)
                    ).scalars().all()
                    
                    # Determine if it's a win (30% chance)
                    is_win = random.random() < 0.3
                    
                    if is_win and coupons:
                        # Select a random coupon
                        selected_coupon = random.choice(coupons)
                        # Get the coupon's assigned icon (based on its position in the list)
                        coupon_index = coupons.index(selected_coupon)
                        icon = SYMBOLS[coupon_index % len(SYMBOLS)]
                        
                        return jsonify({
                            "success": True,
                            "is_win": True,
                            "coupon": {
                                "code": selected_coupon.code,
                                "description": selected_coupon.description,
                                "icon": icon
                            }
                        })
                    else:
                        return jsonify({
                            "success": True,
                            "is_win": False
                        })
                else:
                    return jsonify({
                        "success": False,
                        "error": "Invalid action"
                    }), 400
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        # Handle coupon claim
        code = request.form.get("coupon_code")
        if code and code != "NO_PRIZE":
            try:
                coupon = db.session.execute(
                    db.select(Coupon).where(Coupon.code == code, Coupon.active == True)
                ).scalar_one_or_none()
                
                if not coupon:
                    flash("Invalid coupon code.", "danger")
                elif coupon in current_user.coupons:
                    flash("You already have this coupon!", "info")
                else:
                    current_user.coupons.append(coupon)
                    db.session.commit()
                    flash(f"{coupon.code} added to your account!", "success")
                    return redirect(url_for("dashboard_page"))
            except Exception as e:
                flash(f"Error claiming coupon: {str(e)}", "danger")
        return redirect(url_for("game.slot_machine"))

    # Get active coupons for the slot machine
    try:
        coupons = db.session.execute(
            db.select(Coupon).where(Coupon.active == True)
        ).scalars().all()
        
        slot_data = []
        for i, coupon in enumerate(coupons):
            slot_data.append({
                "code": coupon.code,
                "description": coupon.description,
                "discount_amount": float(coupon.discount_amount),
                "is_percent": coupon.is_percent,
                "minimum_purchase": float(coupon.minimum_purchase) if coupon.minimum_purchase else None,
                "odds": round(100 / len(coupons), 1),  # Equal odds for each coupon
                "icon": SYMBOLS[i % len(SYMBOLS)]  # Assign icons cyclically
            })

        # If no coupons available, add a "no prize" option
        if not slot_data:
            slot_data = [{
                "code": "NO_PRIZE",
                "description": "No prizes available",
                "discount_amount": 0,
                "is_percent": False,
                "minimum_purchase": None,
                "odds": 100.0,
                "icon": SYMBOLS[0]
            }]

        return render_template("slot_machine.html", slot_coupons=slot_data)
    except Exception as e:
        flash(f"Error loading slot machine: {str(e)}", "danger")
        return redirect(url_for("home_page")) 