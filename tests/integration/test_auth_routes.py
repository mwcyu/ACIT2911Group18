from datetime import datetime, timezone, UTC
import pytest
from unittest.mock import MagicMock
from flask import session, current_app, url_for
from tests.conftest import assert_flashed_message
from models import Customer
from db import db
from flask_login import login_user


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


class TestOAuth:
    def test_google_oauth_redirect(self, client):
        """Test Google OAuth redirect"""
        response = client.get("/auth/google")
        assert response.status_code == 302
        assert "accounts.google.com" in response.location

    def test_google_callback_error_handling(self, client):
        """Test Google OAuth error handling"""
        with client:
            response = client.get("/auth/callback/google", follow_redirects=True)
            assert response.status_code == 200  
            assert b"Google OAuth error" in response.data

    def test_github_callback_new_user(self, client, monkeypatch):
        """Test GitHub OAuth callback for new user"""
        class MockResponse:
            def json(self):
                if self.endpoint == "user":
                    return {
                        "id": "12345",
                        "login": "testuser",
                    }
                elif self.endpoint == "user/emails":
                    return [{
                        "email": "test@github.com",
                        "primary": True,
                        "verified": True
                    }]
        
        def mock_get(endpoint):
            response = MockResponse()
            response.endpoint = endpoint
            return response

        mock_github = MagicMock()
        mock_github.authorize_access_token.return_value = {"access_token": "test_token"}
        mock_github.get.side_effect = mock_get

        with client.application.app_context():
            current_app.config['GITHUB_OAUTH_CLIENT'] = mock_github
            
            with client:
                response = client.get("/auth/callback/github", follow_redirects=True)
                assert response.status_code == 200
                assert session.get("customer_name") == "testuser"


class TestLogout:
    def test_logout_clears_session(self, client, test_user):
        """Test logout clears session data"""
        # Log in first
        with client.session_transaction() as sess:
            sess["customer_id"] = test_user.id
            sess["customer_name"] = test_user.name
            sess["cart"] = {}

        with client:
            # Verify we're logged in
            response = client.get("/dashboard", follow_redirects=True)
            assert response.status_code == 200

            # Now logout
            response = client.post("/auth/logout")
            assert response.status_code == 302  # Redirect after logout
            assert session.get("customer_id") is None
            assert session.get("customer_name") is None
            assert session.get("cart") is None

    def test_logout_redirects_to_home(self, client):
        """Test logout redirects to home page"""
        response = client.post("/auth/logout")
        assert response.status_code == 302
        assert "/" in response.location

class TestOAuthEdgeCases:
    def test_google_callback_existing_email(self, client, test_user, monkeypatch, db):
        """Test Google OAuth links account when email matches"""
        mock_google = MagicMock()
        mock_google.authorize_access_token.return_value = {"access_token": "test_token"}
        mock_google.get.return_value.json.return_value = {
            "id": "newgoogleid",
            "email": test_user.email,
            "name": "Google User"
        }

        with client.application.app_context():
            current_app.config['GOOGLE_OAUTH_CLIENT'] = mock_google

            with client:
                response = client.get("/auth/callback/google", follow_redirects=True)
                assert response.status_code == 200

                # Query the user fresh from db instead of refreshing
                updated_user = db.session.scalar(
                    db.select(Customer).where(Customer.id == test_user.id)
                )
                assert updated_user.google_id == "newgoogleid"
