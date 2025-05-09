import pytest
from flask import url_for
from models import Customer
from flask_login import current_user

def test_login_with_valid_credentials(client, test_user):
    """Test login with valid credentials redirects to dashboard"""
    response = client.post("/auth/login", data={
        "phone": test_user.phone,
        "password": "testpass"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Order Summary" in response.data  # Dashboard page header

def test_login_with_wrong_password(client, test_user):
    """Test login with invalid credentials shows error"""
    response = client.post("/auth/login", data={
        "phone": test_user.phone,
        "password": "wrongpass"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid phone number or password." in response.data

def test_register_new_account(client, db):
    """Test registering a new account"""
    response = client.post("/auth/register", data={
        "name": "New User",
        "phone": "123-456-7890",
        "email": "new@test.com",
        "password": "password123"
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Order Summary" in response.data  # Dashboard page after successful registration

    # Verify user was created in database
    user = db.session.execute(db.select(Customer).where(Customer.phone == "123-456-7890")).scalar()
    assert user is not None
    assert user.name == "New User"

def test_register_duplicate_phone(client, test_user):
    """Test registering with an existing phone number fails"""
    response = client.post("/auth/register", data={
        "name": "Another User",
        "phone": test_user.phone,  # Use existing phone number
        "email": "another@test.com",
        "password": "password123"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"This phone number already has an account" in response.data

def test_logout(logged_in_client):
    """Test logout redirects to home and clears session"""
    response = logged_in_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data  # Login link appears in nav after logout

def test_forgot_password(client, test_user):
    """Test forgot password functionality"""
    response = client.post("/auth/forgot-password", data={
        "phone": test_user.phone
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"A password reset link has been sent to your email." in response.data

def test_invalid_forgot_password(client):
    """Test forgot password with non-existent phone"""
    response = client.post("/auth/forgot-password", data={
        "phone": "999-999-9999"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"No account found with that phone number." in response.data

def test_reset_password_with_invalid_token(client):
    """Test reset password with invalid token"""
    response = client.get("/auth/reset-password/invalid-token", follow_redirects=True)
    assert response.status_code == 200
    assert b"The reset link is invalid or expired." in response.data