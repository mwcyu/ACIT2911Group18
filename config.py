import os
from dotenv import load_dotenv
import forms
from flask_security import uia_phone_mapper

load_dotenv()  # Load from .env

class Config:

    # Use the built-in phone mapper (normalizes via phonenumbers)
    SECURITY_USER_IDENTITY_ATTRIBUTES = [
        {"phone": {"mapper": uia_phone_mapper}}
    ]
    SECURITY_PHONE_REGION_DEFAULT = "CA"
    SECRET_KEY = os.getenv("SECRET_KEY", "default_key")
    
    # Mail config
    MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 25))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "false").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_USERNAME")
    # Security Core
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", "some-random-salt")
    SECURITY_PASSWORD_HASH = "pbkdf2_sha512"

    # Features
    SECURITY_REGISTERABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_TRACKABLE = True
    SECURITY_CONFIRMABLE = False
    SECURITY_TWO_FACTOR = False
    SECURITY_TWO_FACTOR_REQUIRED = False
    SECURITY_TWO_FACTOR_ENABLED_METHODS = ["email", "authenticator"]
    SECURITY_TWO_FACTOR_EMAIL_SUBJECT = "Your Login Code"
    SECURITY_TOTP_SECRETS = {
        '1': os.getenv('TOTP_SECRET', 'base32secret3232')
    }
    SECURITY_TOTP_ISSUER = os.getenv('TOTP_ISSUER', 'ACIT2911Group18')
    SECURITY_EMAIL_SENDER = os.getenv("MAIL_USERNAME")
    # Flask-Security-Too
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_CHANGEABLE = True
    SECURITY_LOGIN_WITHOUT_CONFIRMATION = True
    SECURITY_FORMS = {
    "register_form": forms.ExtendedRegisterForm,
    "login_form": forms.PhoneLoginForm
}
    SECURITY_POST_LOGIN_VIEW = "/dashboard"
    
    # DEBUGING
    
    DEBUG = True
    SECURITY_DEBUG = True
    SECURITY_MSG_LOG_REGISTER = True

# Optional
    OAUTH2_PROVIDERS = {
    # Google OAuth 2.0 documentation:
    # https://developers.google.com/identity/protocols/oauth2/web-server#httprest
    'google': {
        'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
        'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'token_url': 'https://accounts.google.com/o/oauth2/token',
        'userinfo': {
            'url': 'https://www.googleapis.com/oauth2/v3/userinfo',
            'email': lambda json: json['email'],
        },
        'scopes': ['https://www.googleapis.com/auth/userinfo.email'],
    },

    # GitHub OAuth 2.0 documentation:
    # https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps
    'github': {
        'client_id': os.environ.get('GITHUB_CLIENT_ID'),
        'client_secret': os.environ.get('GITHUB_CLIENT_SECRET'),
        'authorize_url': 'https://github.com/login/oauth/authorize',
        'token_url': 'https://github.com/login/oauth/access_token',
        'userinfo': {
            'url': 'https://api.github.com/user/emails',
            'email': lambda json: json[0]['email'],
        },
        'scopes': ['user:email'],
    },
}
