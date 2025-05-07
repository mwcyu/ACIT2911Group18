import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env

class BaseConfig:
    """Base configuration settings"""
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key-change-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT", "default-salt-change-in-production")
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Mail
    MAIL_SERVER = os.getenv("MAIL_SERVER", "localhost")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 25))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "false").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")
    
    # OAuth
    GITHUB_OAUTH_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_OAUTH_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
    GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

class DevelopmentConfig(BaseConfig):
    """Development configuration settings"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///project1.db"
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    
class TestingConfig(BaseConfig):
    """Testing configuration settings"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    
class ProductionConfig(BaseConfig):
    """Production configuration settings"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///project1.db")
    
    # Production security settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    
    # Logging
    LOG_LEVEL = "INFO"

# Configure based on environment
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}

Config = config[os.getenv("FLASK_ENV", "default")]