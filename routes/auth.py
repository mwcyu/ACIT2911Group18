from flask import Blueprint, request, render_template, redirect, url_for, session, flash, current_app, make_response
from flask_login import login_user, logout_user, login_required, current_user
from flask_security import login_user
from models import Customer
from db import db
from email_utils import send_password_reset_email, verify_reset_token
from flask_security.utils import login_user

auth_bp = Blueprint("auth", __name__, template_folder="../templates")

@auth_bp.route("/github")
def github_oauth():
    github = current_app.config['GITHUB_OAUTH_CLIENT']
    return github.authorize_redirect(url_for('auth.github_callback', _external=True))

@auth_bp.route("/callback/github")
def github_callback():
    github = current_app.config['GITHUB_OAUTH_CLIENT']
    token = github.authorize_access_token()
    profile = github.get('user').json()

    github_id = str(profile['id'])
    stmt = db.select(Customer).where(Customer.github_id == github_id)
    customer = db.session.execute(stmt).scalar_one_or_none()

    if not customer:
        email_data = github.get('user/emails').json()
        primary_email = next((e["email"] for e in email_data if e.get("primary") and e.get("verified")), None)

        customer = Customer(
            github_id=github_id,
            name=profile.get("login"),
            email=primary_email,
            active=True
        )
        db.session.add(customer)
        db.session.commit()

    login_user(customer, remember=True, authn_via=["github"])  # Use Flask-Security login_user

    # Flask-Security handles session, so no need to set session["customer_id"] etc.
    return redirect(url_for("dashboard_page"))