from flask import (
    Blueprint, request, render_template, redirect,
    url_for, session, flash, current_app
)
from flask_login import (
    login_user, logout_user,
    login_required, current_user
)
from forms import (
    LoginForm, RegisterForm,
    ForgotPasswordForm, ResetPasswordForm,
    TwoFactorForm
)
from models import Customer
from db import db
from datetime import datetime, UTC

auth_bp = Blueprint("auth", __name__, template_folder="../templates")


@auth_bp.route("/github")
def github_oauth():
    github = current_app.config['GITHUB_OAUTH_CLIENT']
    return github.authorize_redirect(
        url_for('auth.github_callback', _external=True)
    )


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
        primary_email = next(
            (e["email"] for e in email_data
             if e.get("primary") and e.get("verified")),
            None
        )
        customer = Customer(
            github_id=github_id,
            name=profile.get("login"),
            email=primary_email
        )
        db.session.add(customer)
        db.session.commit()

    login_user(customer)
    session.update({
        "customer_id": customer.id,
        "customer_name": customer.name,
        "cart": session.get("cart", {})
    })
    return redirect(url_for("dashboard_page"))


@auth_bp.route("/google")
def google_oauth():
    google = current_app.config['GOOGLE_OAUTH_CLIENT']
    redirect_uri = url_for('auth.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)


@auth_bp.route("/callback/google")
def google_callback():
    google = current_app.config['GOOGLE_OAUTH_CLIENT']
    try:
        token = google.authorize_access_token()
    except Exception as e:
        flash(f"Google OAuth error: {str(e)}", "danger")
        return redirect(url_for("auth.login"))
    
    user_info = google.get('userinfo').json()
    google_id = str(user_info.get('id'))
    email = user_info.get('email')
    name = user_info.get('name', email.split('@')[0]) # Use name or derive from email

    # Check if user exists by google_id
    customer = db.session.scalar(
        db.select(Customer).where(Customer.google_id == google_id)
    )

    if not customer and email:
        # Check if user exists by email (if google_id didn't match)
        customer = db.session.scalar(
            db.select(Customer).where(Customer.email == email)
        )
        if customer:
            # Link Google ID to existing email-matched account
            customer.google_id = google_id
            db.session.commit()

    if not customer:
        # Create new customer if no match by google_id or email
        customer = Customer(
            google_id=google_id,
            name=name,
            email=email,
            # Initialize with a placeholder phone value that uses the google ID
            # This is needed since phone is required but we don't get it from Google
            phone=f"google_{google_id}"
        )
        db.session.add(customer)
        db.session.commit()

    login_user(customer)
    session.update({
        "customer_id": customer.id,
        "customer_name": customer.name,
        "cart": session.get("cart", {})
    })
    flash("Successfully logged in with Google!", "success")
    return redirect(url_for("dashboard_page"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        phone = form.phone.data.strip()
        password = form.password.data.strip()
        customer = db.session.scalar(
            db.select(Customer).where(Customer.phone == phone)
        )

        if customer and customer.check_password(password):
            # lazy-import here to avoid circular import
            from email_utils import generate_and_send_otp

            generate_and_send_otp(customer.email)
            session['2fa_user_id'] = customer.id
            session['2fa_purpose'] = 'login'
            flash(
                "A 6-digit code has been sent to your email. "
                "Please enter it below.",
                "info"
            )
            return redirect(url_for("auth.two_factor"))

        flash("Invalid phone number or password.", "danger")

    return render_template("login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        phone = form.phone.data.strip()
        email = form.email.data.strip()
        password = form.password.data.strip()

        exists = db.session.scalar(
            db.select(Customer).where(Customer.phone == phone)
        )
        if exists:
            flash("This phone number already has an account", "warning")
            return render_template("register.html", form=form)

        new_customer = Customer(name=name, phone=phone, email=email)
        new_customer.set_password(password)
        db.session.add(new_customer)
        db.session.commit()

        # Send 2FA email
        from email_utils import generate_and_send_otp

        generate_and_send_otp(email)
        session['2fa_user_id'] = new_customer.id
        session['2fa_purpose'] = 'register'


        flash(
            "A 6-digit code has been sent to your email. "
            "Please enter it below to complete registration.",
            "info"
        )
        return redirect(url_for('auth.two_factor'))

    return render_template("register.html", form=form)



@auth_bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    session.clear()
    response = redirect(url_for("home_page"))
    return response


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        phone = form.phone.data.strip()
        customer = db.session.scalar(
            db.select(Customer).where(Customer.phone == phone)
        )

        if customer:
            # lazy-import here too
            from email_utils import send_password_reset_email

            send_password_reset_email(customer)
            flash("A password reset link has been sent to your email.", "info")
            return redirect(url_for("auth.login"))

        flash("No account found with that phone number.", "warning")

    return render_template("forgot_password.html", form=form)


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    # lazy-import again
    from email_utils import verify_reset_token

    phone = verify_reset_token(token)
    if not phone:
        flash("The reset link is invalid or expired.", "danger")
        return redirect(url_for("auth.forgot_password"))

    customer = db.session.scalar(
        db.select(Customer).where(Customer.phone == phone)
    )
    if not customer:
        flash("Invalid user.", "danger")
        return redirect(url_for("auth.login"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        customer.set_password(form.password.data.strip())
        db.session.commit()
        flash("Your password has been updated.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", form=form)


@auth_bp.route("/two-factor", methods=["GET", "POST"])
def two_factor():
    form = TwoFactorForm()
    user_id = session.get("2fa_user_id")
    purpose = session.get("2fa_purpose", "login")  # default fallback
    if not user_id:
        flash("Please log in first.", "warning")
        return redirect(url_for("auth.login"))

    if form.validate_on_submit():
        code_submitted = form.code.data
        otp = session.get("2fa_otp")
        expires_ts = session.get("2fa_expires", 0)

        if datetime.now(UTC).timestamp() > expires_ts:
            flash("Your code has expired. Please try again.", "danger")
            session.pop("2fa_user_id", None)
            session.pop("2fa_purpose", None)
            return redirect(url_for(f"auth.{purpose}"))  # back to login or register

        if code_submitted == otp:
            customer = db.session.get(Customer, user_id)
            login_user(customer)

            for key in ("2fa_user_id", "2fa_otp", "2fa_expires", "2fa_purpose"):
                session.pop(key, None)

            session.update({
                "customer_id": customer.id,
                "customer_name": customer.name,
                "cart": session.get("cart", {})
            })

            flash("Two-factor authentication successful!", "success")
            return redirect(url_for("dashboard_page"))

        flash("Invalid authentication code.", "danger")

    return render_template("two_factor.html", form=form)

