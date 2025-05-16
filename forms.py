from flask_security.forms import RegisterForm, LoginForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class ExtendedRegisterForm(RegisterForm):
    name = StringField("Name", validators=[DataRequired()])
    phone = StringField("Phone", validators=[DataRequired(), Length(min=8)])

class PhoneLoginForm(LoginForm):
    phone = StringField("Phone", validators=[DataRequired(), Length(min=8)])
    password = PasswordField("Password", validators=[DataRequired()])
    identity = StringField(
        "Phone",
        validators=[DataRequired(message="Please enter your phone number"),
                    Length(min=8, message="Phone must be at least 8 digits")]
    )

    submit = SubmitField("Login")