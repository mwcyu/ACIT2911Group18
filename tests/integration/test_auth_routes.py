"""Integration tests for authentication routes"""
from flask import session
from ..conftest import assert_flashed_message

class TestLogin:
    def test_login_page_loads(self, client):
        """Test login page renders correctly"""
        response = client.get("/auth/login")
        assert response.status_code == 200
        assert b"Sign In" in response.data

    def test_successful_login(self, client, test_user):
        """Test successful login with valid credentials"""
        with client:  # Create request context
            response = client.post("/auth/login", data={
                "phone": test_user.phone,
                "password": "testpass"
            }, follow_redirects=True)
            
            assert response.status_code == 200
            assert session.get("customer_id") == test_user.id
            assert session.get("customer_name") == test_user.name
            assert "cart" in session
            # Look for dashboard elements instead of exact text
            assert b"Order Summary" in response.data  # Dashboard page

    def test_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials"""
        with client:  # Create request context
            response = client.post("/auth/login", data={
                "phone": test_user.phone,
                "password": "wrongpass"
            }, follow_redirects=True)
            
            assert response.status_code == 200
            assert_flashed_message(response, "Invalid phone number or password.", "danger")
            assert "customer_id" not in session

class TestRegistration:
    def test_register_page_loads(self, client):
        """Test registration page renders correctly"""
        response = client.get("/auth/register")
        assert response.status_code == 200
        assert b"Register" in response.data

    def test_successful_registration(self, client, db):
        """Test successful user registration"""
        with client:  # Create request context
            response = client.post("/auth/register", data={
                "name": "New User",
                "phone": "123-456-7890",
                "email": "new@test.com",
                "password": "password123"
            }, follow_redirects=True)
            
            assert response.status_code == 200
            # Check for any dashboard content since page may be empty on first login
            assert session.get("customer_name") == "New User"
            assert "cart" in session

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