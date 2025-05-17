import random
from datetime import datetime, timedelta, UTC
from flask import current_app, url_for, session
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer


def generate_reset_token(data):
    """
    Generate a secure token for password reset using the app's secret key
    Args:
        data: The data to be encoded in the token (usually user phone)
    Returns:
        str: An encrypted token
    """
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps(data, salt="password-reset")


def verify_reset_token(token, max_age=900):
    """
    Verify and decode a password reset token
    Args:
        token: The token to verify
        max_age: Maximum age of token in seconds (default 15 minutes)
    Returns:
        The decoded data or None if invalid/expired
    """
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        return s.loads(token, salt="password-reset", max_age=max_age)
    except Exception:
        return None


def send_password_reset_email(customer):
    """
    Send a password reset email to a customer
    Args:
        customer: Customer object containing email, phone, and name
    """
    # Generate reset token using customer's phone
    token = generate_reset_token(customer.phone)
    # Create the full reset URL
    reset_url = url_for("auth.reset_password", token=token, _external=True)

    # For testing without sending real email
    print("RESET LINK:", reset_url)

    # Create email message
    msg = Message(
        subject="Reset Your Password",
        recipients=[customer.email],
        body=render_reset_email(customer.name, reset_url),
    )

    # Get mail extension from current app
    mail = current_app.extensions.get("mail")
    if mail:
        try:
            mail.send(msg)
        except Exception as e:
            print("Failed to send email:", e)
    else:
        print("Mail extension not initialized.")


def render_reset_email(name, reset_url):
    """
    Generate the body text for password reset email
    Args:
        name: Customer's name
        reset_url: The password reset URL
    Returns:
        str: Formatted email body text
    """
    return f"""Hello {name},

You requested to reset your password.

Click the link below to reset it:
{reset_url}

If you didn't request this, just ignore this message.

Thanks,
Your Store Team
"""

def generate_and_send_otp(user_email):
    # generate a 6-digit code
    otp = f"{random.randint(0, 999999):06d}"
    # store in session with expiry (UTC)
    session['2fa_otp']      = otp
    session['2fa_expires']  = (datetime.now(UTC) + timedelta(minutes=5)).timestamp()
    # send it
    msg = Message("Your Login Code", recipients=[user_email])
    msg.body = f"Your two-factor authentication code is: {otp}\nIt expires in 5 minutes."
    
    # Get mail extension from current app
    mail = current_app.extensions.get("mail")
    if mail:
        try:
            mail.send(msg)
        except Exception as e:
            print("Failed to send email:", e)
    else:
        print("Mail extension not initialized.")