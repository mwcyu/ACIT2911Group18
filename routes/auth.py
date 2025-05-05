from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from flask_login import login_user, logout_user, login_required

from forms import LoginForm, RegisterForm, ForgotPasswordForm, ResetPasswordForm

from models import Customer
from db import db

from email_utils import send_password_reset_email, verify_reset_token

auth_bp = Blueprint("auth", __name__, template_folder="../templates")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # this is build in method
        phone = form.phone.data.strip()
        password = form.password.data.strip()
        
        stmt = db.select(Customer).where(Customer.phone == phone)
        customer = db.session.execute(stmt).scalar_one_or_none()
        
        if customer and customer.password == password:
            login_user(customer)
            
            print("---- SESSION DATA ----")
            print(dict(session))
            return redirect(url_for("dashboard_page"))
        else:
            flash("Invalid phone number or password.", "danger")

    return render_template("login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST":
        name = form.name.data.strip()
        phone = form.phone.data.strip()
        email = form.email.data.strip()
        password = form.password.data.strip()

        stmt = db.select(Customer).where(Customer.phone == phone)
        customer = db.session.execute(stmt).scalar_one_or_none()

        if customer:
            flash("This phone number already has an account", "warning")
            return render_template("register.html", form=form)

        new_customer = Customer(name=name, phone=phone, email=email, password=password)
        db.session.add(new_customer)
        db.session.commit()
        
        login_user(new_customer)

        return redirect(url_for('dashboard_page'))

    return render_template("register.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    session.clear()
    logout_user()
    print(dict(session))
    return redirect(url_for("home_page"))



@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        phone = form.phone.data.strip()
        customer = db.session.scalar(db.select(Customer).where(Customer.phone == phone))

        if customer:
            send_password_reset_email(customer)
            flash("A password reset link has been sent to your email.", "info")
            return redirect(url_for("auth.login"))
        else:
            flash("No account found with that phone number.", "warning")

    return render_template("forgot_password.html", form=form)

@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    phone = verify_reset_token(token)
    if not phone:
        flash("The reset link is invalid or expired.", "danger")
        return redirect(url_for("auth.forgot_password"))

    customer = db.session.scalar(db.select(Customer).where(Customer.phone == phone))
    if not customer:
        flash("Invalid user.", "danger")
        return redirect(url_for("auth.login"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        customer.password = form.password.data.strip()
        db.session.commit()
        flash("Your password has been updated.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", form=form)