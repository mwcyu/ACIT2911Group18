from flask import Blueprint, request, render_template, redirect, url_for, session
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from models import Customer
from db import db

auth_bp = Blueprint("auth", __name__, template_folder="../templates")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        raw_password = request.form["password"]

        if db.session.execute(db.select(Customer).where(Customer.phone == phone)).scalar():
            return render_template("register.html", error="Phone already registered")

        hashed_password = generate_password_hash(raw_password)
        customer = Customer(name=name, phone=phone, password=hashed_password)

        db.session.add(customer)
        db.session.commit()

        login_user(customer)
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form["phone"]
        password = request.form["password"]

        customer = db.session.execute(db.select(Customer).where(Customer.phone == phone)).scalar_one_or_none()

        if customer and check_password_hash(customer.password, password):
            login_user(customer)
            return redirect(url_for("dashboard"))

        return render_template("login.html", error="Invalid phone or password")

    return render_template("login.html")

# ─── Logout Route ──────────────────────────────────────────────

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
