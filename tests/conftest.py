# tests/conftest.py

import pytest
from app import create_app
from db import db as _db
from models import Customer, Category, Product, Season
from flask_login import login_user
from datetime import datetime, UTC
from flask import session
import email_utils

# ----------------------
# Shared test helpers
# ----------------------

def assert_flashed_message(response, message: str, category: str = None):
    """Check for flashed messages in response HTML"""
    decoded = response.data.decode()
    if category:
        assert f"alert alert-{category}" in decoded
    assert message in decoded

# ----------------------
# Flask app & database setup
# ----------------------

@pytest.fixture()
def app():
    """Create a Flask app instance with test config"""
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_ENGINE_OPTIONS": {
            "connect_args": {"check_same_thread": False}
        },
        "SECRET_KEY": "testsecret",
        "WTF_CSRF_ENABLED": False,
        "LOGIN_DISABLED": False,
    }

    flask_app = create_app(test_config)

    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.session.close()  # Close any active sessions
        _db.engine.dispose()  # Release connection pool
        _db.drop_all()

@pytest.fixture
def db(app):
    """Return the active SQLAlchemy db instance"""
    return _db

@pytest.fixture
def client(app):
    """Return Flask test client"""
    return app.test_client()

# ----------------------
# Test Data Fixtures
# ----------------------

@pytest.fixture
def test_category(db):
    category = Category(name="Test Category")
    db.session.add(category)
    db.session.commit()
    return category

@pytest.fixture
def test_season(db):
    season = Season(name="Test Season", active=True)
    db.session.add(season)
    db.session.commit()
    return season

@pytest.fixture
def test_product(db, test_category, test_season):
    product = Product(
        name="Test Product",
        price=9.99,
        available=10,
        in_season=True,
        category=test_category,
        season=test_season
    )
    db.session.add(product)
    db.session.commit()
    return product

@pytest.fixture
def test_user(db):
    user = Customer(name="Test User", phone="555-000-0000", email="test@example.com")
    user.set_password("testpass")
    db.session.add(user)
    db.session.commit()
    return user

# ----------------------
# Login Simulation
# ----------------------

@pytest.fixture
def logged_in_client(client, test_user, app):
    """Simulate a logged-in user in the test client"""
    with app.test_request_context():
        login_user(test_user)

    with client.session_transaction() as sess:
        sess["_user_id"] = str(test_user.id)

    return client

# ----------------------
# Monkeypatch OTP for 2FA
# ----------------------

@pytest.fixture(autouse=True)
def stub_generate_and_send_otp(monkeypatch):
    """
    Replace generate_and_send_otp() so that it always sets a known OTP in session.
    Prevents email sending during tests.
    """
    def fake_generate_and_send_otp(email_address):
        session['2fa_otp'] = '123456'
        session['2fa_expires'] = datetime.now(UTC).timestamp() + 300

    monkeypatch.setattr(email_utils, 'generate_and_send_otp', fake_generate_and_send_otp)