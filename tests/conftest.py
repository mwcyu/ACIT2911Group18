# tests/conftest.py
import pytest
from app import app as flask_app
from db import db as _db
from models import Customer, Category, Product, Season
from flask_login import LoginManager, login_user
from datetime import datetime, UTC
import email_utils

from flask import session


def assert_flashed_message(response, message: str, category: str = None):
    """Check for flashed messages in response HTML"""
    decoded = response.data.decode()
    if category:
        assert f"alert alert-{category}" in decoded
    assert message in decoded

@pytest.fixture()
def app():
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:","SQLALCHEMY_ENGINE_OPTIONS": {
            "connect_args": {"check_same_thread": False}
        },
        "SECRET_KEY": "testsecret",
        "WTF_CSRF_ENABLED": False,
        "LOGIN_DISABLED": False
    })

    with flask_app.app_context():
        _db.create_all()
        yield flask_app
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def test_category(db):
    category = Category(name="Test Category")
    db.session.add(category)
    db.session.commit()
    return category

@pytest.fixture
def test_season(db):
    season = Season(name="Test Season")
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


@pytest.fixture
def logged_in_client(client, test_user, app):
    with app.test_request_context():
        login_user(test_user)

    # Use the test client to log in session-wise
    with client.session_transaction() as session:
        session["_user_id"] = str(test_user.id)

    return client

@pytest.fixture(autouse=True)
def stub_generate_and_send_otp(monkeypatch):
    """
    Replace generate_and_send_otp() so that it simply
    writes a deterministic 6-digit code into Flask's session.
    """
    def fake_generate_and_send_otp(email_address):
        session['2fa_otp'] = '123456'
        # expire 5 minutes from now
        session['2fa_expires'] = datetime.now(UTC).timestamp() + 300

    monkeypatch.setattr(email_utils, 'generate_and_send_otp', fake_generate_and_send_otp)