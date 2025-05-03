from flask import Blueprint, request, render_template, redirect, url_for, session
from flask_login import login_user, logout_user, login_required

from models import Customer
from db import db

auth_bp = Blueprint("auth", __name__, template_folder="../templates")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error_message = None
    if request.method == "POST":
        phone = request.form.get("phone", '').strip()
        password = request.form.get("password", '').strip()

        stmt = db.select(Customer).where(Customer.phone == phone)
        customer = db.session.execute(stmt).scalar_one_or_none()
        
        # Hello
        if customer and customer.password == password:
            login_user(customer)

            print("---- SESSION DATA ----")
            print(dict(session))
            print("----------------------")

            return redirect(url_for('dashboard_page'))
        else:
            error_message = "Invalid phone number or password. Please try again."

    return render_template("login.html", error_message=error_message)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get('name').strip()
        phone = request.form.get('phone').strip()
        password = request.form.get('password').strip()

        stmt = db.select(Customer).where(Customer.phone == phone)
        customer = db.session.execute(stmt).scalar_one_or_none()

        if customer:
            return render_template("register.html", error_message="This phone number already has an account")

        new_customer = Customer(name=name, phone=phone, password=password)
        db.session.add(new_customer)
        db.session.commit()
        
        login_user(new_customer)

        return redirect(url_for('dashboard_page'))

    return render_template("register.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    print(dict(session))
    return redirect(url_for("home_page"))