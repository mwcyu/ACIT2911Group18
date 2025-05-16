from datetime import datetime, timezone, UTC
import pytest
from flask import session
from tests.conftest import assert_flashed_message


class TestLogin:
    def test_login_page_loads(self, client):
        """Test login page renders correctly"""
        response = client.get("/auth/login")
        assert response.status_code == 200
        assert b"Sign In" in response.data

    def test_successful_login(self, client, test_user):
        """Test successful login triggers 2FA"""
        with client:
            response = client.post("/auth/login", data={
                "phone": test_user.phone,
                "password": "testpass"
            }, follow_redirects=True)

            assert response.status_code == 200
            assert b"A 6-digit code has been sent to your email." in response.data
            assert session.get("2fa_user_id") == test_user.id
            assert session.get("2fa_purpose") == "login"

    def test_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials"""
        with client:
            response = client.post("/auth/login", data={
                "phone": test_user.phone,
                "password": "wrongpass"
            }, follow_redirects=True)

            assert_flashed_message(response, "Invalid phone number or password.", "danger")
            assert "customer_id" not in session


class TestRegistration:
    def test_register_page_loads(self, client):
        """Test registration page renders correctly"""
        response = client.get("/auth/register")
        assert response.status_code == 200
        assert b"Register" in response.data

    def test_successful_registration(self, client, db):
        """Test successful registration triggers 2FA"""
        with client:
            response = client.post("/auth/register", data={
                "name": "New User",
                "phone": "123-456-7890",
                "email": "new@test.com",
                "password": "password123"
            }, follow_redirects=True)

            assert response.status_code == 200
            assert b"A 6-digit code has been sent to your email." in response.data
            assert session.get("2fa_purpose") == "register"
            assert session.get("2fa_user_id") is not None

    def test_duplicate_phone_registration(self, client, test_user):
        """Test registration with existing phone number"""
        response = client.post("/auth/register", data={
            "name": "Another User",
            "phone": test_user.phone,
            "email": "another@test.com",
            "password": "password123"
        }, follow_redirects=True)

        assert response.status_code == 200
        assert_flashed_message(response, "This phone number already has an account", "warning")


class TestTwoFactor:
    def test_two_factor_login_success(self, client, test_user):
        """Simulate correct OTP submission to complete login"""
        with client.session_transaction() as sess:
            sess["2fa_user_id"] = test_user.id
            sess["2fa_otp"] = "123456"
            sess["2fa_expires"] = datetime.now(UTC).timestamp() + 60
            sess["2fa_purpose"] = "login"

        response = client.post("/auth/two-factor", data={
            "code": "123456"
        }, follow_redirects=True)

        assert response.status_code == 200
        assert_flashed_message(response, "Two-factor authentication successful!", "success")

        with client.session_transaction() as sess:
            assert sess.get("customer_id") == test_user.id
            assert sess.get("customer_name") == test_user.name

    def test_two_factor_invalid_code(self, client, test_user):
        """Simulate wrong OTP"""
        with client.session_transaction() as sess:
            sess["2fa_user_id"] = test_user.id
            sess["2fa_otp"] = "123456"
            sess["2fa_expires"] = datetime.now(UTC).timestamp() + 60
            sess["2fa_purpose"] = "login"

        response = client.post("/auth/two-factor", data={
            "code": "000000"
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b"Invalid authentication code." in response.data

        with client.session_transaction() as sess:
            assert sess.get("customer_id") is None


class TestPasswordReset:
    def test_forgot_password_page(self, client):
        """Test forgot password page renders"""
        response = client.get("/auth/forgot-password")
        assert response.status_code == 200
        assert b"Forgot Password" in response.data

    def test_forgot_password_valid_phone(self, client, test_user):
        """Test forgot password with valid phone"""
        response = client.post("/auth/forgot-password", data={
            "phone": test_user.phone
        }, follow_redirects=True)

        assert response.status_code == 200
        assert_flashed_message(response,
            "A password reset link has been sent to your email.", "info")

    def test_forgot_password_invalid_phone(self, client):
        """Test forgot password with invalid phone"""
        response = client.post("/auth/forgot-password", data={
            "phone": "999-999-9999"
        }, follow_redirects=True)

        assert response.status_code == 200
        assert_flashed_message(response,
            "No account found with that phone number.", "warning")

    def test_reset_password_invalid_token(self, client):
        """Test reset password with invalid token"""
        response = client.get("/auth/reset-password/invalid-token",
                              follow_redirects=True)

        assert response.status_code == 200
        assert_flashed_message(response,
            "The reset link is invalid or expired.", "danger")
