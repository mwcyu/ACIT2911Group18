from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import InputRequired, DataRequired, Length, Regexp

class LoginForm(FlaskForm):
    phone = StringField("Phone", validators=[InputRequired(), Length(min=8)])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])
    phone = StringField("Phone", validators=[InputRequired(), Length(min=8)])
    email = EmailField("Email", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6)])
    submit = SubmitField("Register")

class ForgotPasswordForm(FlaskForm):
    phone = StringField("Phone", validators=[InputRequired(), Length(min=8)])
    submit = SubmitField("Reset Password")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[InputRequired(), Length(min=6)])
    submit = SubmitField("Update Password")

class TwoFactorForm(FlaskForm):
    code = StringField(
        "Authentication Code",
        validators=[
            DataRequired(),
            Length(6, 6, message="Code must be 6 digits"),
            Regexp(r"^\d{6}$", message="Digits only")
        ],
    )
    submit = SubmitField("Verify")