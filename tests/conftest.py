# tests/conftest.py
import pytest
from app import app as flask_app
from db import db as _db
from models import Customer, Category


@pytest.fixture()
def app():
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
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
def test_user(db):
    user = Customer(name="Test User", phone="555-000-0000", email="test@example.com")
    user.set_password("testpass")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def logged_in_client(client, test_user):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
        sess['_fresh'] = True
    return client
