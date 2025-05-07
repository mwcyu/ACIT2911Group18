from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField, EmailField, DecimalField, IntegerField
from wtforms.validators import InputRequired, Length, Email, NumberRange, ValidationError
import re

def phone_number_check(form, field):
    """Custom validator for phone numbers"""
    pattern = re.compile(r'^\d{3}-\d{3}-\d{4}$')
    if not pattern.match(field.data.strip()):
        raise ValidationError('Phone number must be in format: XXX-XXX-XXXX')

class LoginForm(FlaskForm):
    phone = StringField("Phone", validators=[
        InputRequired(),
        Length(min=8),
        phone_number_check
    ])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[
        InputRequired(),
        Length(min=2, max=50)
    ])
    phone = StringField("Phone", validators=[
        InputRequired(),
        Length(min=8),
        phone_number_check
    ])
    email = EmailField("Email", validators=[
        InputRequired(),
        Email(message="Invalid email address")
    ])
    password = PasswordField("Password", validators=[
        InputRequired(),
        Length(min=8, message="Password must be at least 8 characters long")
    ])
    submit = SubmitField("Register")

class ForgotPasswordForm(FlaskForm):
    phone = StringField("Phone", validators=[
        InputRequired(),
        Length(min=8),
        phone_number_check
    ])
    submit = SubmitField("Reset Password")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[
        InputRequired(),
        Length(min=8, message="Password must be at least 8 characters long")
    ])
    submit = SubmitField("Update Password")

class ProductForm(FlaskForm):
    name = StringField("Product Name", validators=[
        InputRequired(),
        Length(min=2, max=100)
    ])
    price = DecimalField("Price", validators=[
        InputRequired(),
        NumberRange(min=0)
    ])
    available = IntegerField("Quantity Available", validators=[
        InputRequired(),
        NumberRange(min=0)
    ])
    submit = SubmitField("Submit")

def init_csrf(app):
    """Initialize CSRF protection"""
    csrf = CSRFProtect()
    csrf.init_app(app)
