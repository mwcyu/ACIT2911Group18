from flask import current_app, url_for
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer


def generate_reset_token(data):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return s.dumps(data, salt="password-reset")


def verify_reset_token(token, max_age=900):
    s = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        return s.loads(token, salt="password-reset", max_age=max_age)
    except Exception:
        return None


def send_password_reset_email(customer):
    token = generate_reset_token(customer.phone)
    reset_url = url_for("auth.reset_password", token=token, _external=True)

    # For testing without sending real email
    print("RESET LINK:", reset_url)

    msg = Message(
        subject="Reset Your Password",
        recipients=[customer.email],
        body=render_reset_email(customer.name, reset_url),
    )

    # Use current_app's mail instance (avoids circular import)
    mail = current_app.extensions.get("mail")
    if mail:
        try:
            mail.send(msg)
        except Exception as e:
            print("Failed to send email:", e)
    else:
        print("Mail extension not initialized.")


def render_reset_email(name, reset_url):
    return f"""Hello {name},

You requested to reset your password.

Click the link below to reset it:
{reset_url}

If you didn’t request this, just ignore this message.

Thanks,
Your Store Team
"""
