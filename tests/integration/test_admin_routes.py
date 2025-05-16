"""Integration tests for admin functionality"""
import pytest
from flask import session
from models import Product
from ..conftest import assert_flashed_message

class TestAdminDashboard:
    def test_admin_dashboard_access(self, logged_in_client, test_user, db):
        """Test admin dashboard access control"""
        # Regular user should not have access
        response = logged_in_client.get("/admin/dashboard")
        assert response.status_code == 403
        
        # Make user an admin
        test_user.is_admin = True
        db.session.commit()
        
        # Admin should have access
        response = logged_in_client.get("/admin/dashboard")
        assert response.status_code == 200
        assert b"Admin Dashboard" in response.data

    def test_admin_dashboard_content(self, logged_in_client, test_user, test_product, db):
        """Test admin dashboard displays correct content"""
        test_user.is_admin = True
        db.session.commit()
        
        with logged_in_client.session_transaction() as sess:
            sess['user_id'] = test_user.id
        response = logged_in_client.get("/admin/dashboard")
        assert response.status_code == 200
        assert test_product.name.encode() in response.data
        assert test_product.category.name.encode() in response.data
        
        # Check for season toggle button
        if test_product.in_season:
            assert b"Remove" in response.data
        else:
            assert b"Add" in response.data

class TestSeasonalToggle:
    def test_toggle_season_as_admin(self, logged_in_client, test_user, test_product, db):
        """Test toggling product seasonal status as admin"""
        test_user.is_admin = True
        db.session.commit()
        initial_status = test_product.in_season
        
        response = logged_in_client.get(
            f"/admin/toggle_season/{test_product.id}",
            follow_redirects=True
        )
        assert response.status_code == 200
        
        # Verify product status was toggled
        db.session.refresh(test_product)
        assert test_product.in_season != initial_status

    def test_toggle_season_as_regular_user(self, logged_in_client, test_product):
        """Test toggling product seasonal status as regular user"""
        response = logged_in_client.get(
            f"/admin/toggle_season/{test_product.id}",
            follow_redirects=True
        )
        assert response.status_code == 403

    def test_toggle_season_nonexistent_product(self, logged_in_client, test_user, db):
        """Test toggling season for non-existent product"""
        test_user.is_admin = True
        db.session.commit()
        
        response = logged_in_client.get("/admin/toggle_season/99999")
        assert response.status_code == 404

class TestAdminAPI:
    def test_make_user_admin(self, logged_in_client, test_user, db):
        """Test API endpoint to toggle admin status"""
        test_user.is_admin = True
        db.session.commit()
        
        # Create another user to make admin
        from models import Customer
        new_user = Customer(
            name="Test Admin",
            phone="555-111-2222",
            email="admin@test.com"
        )
        db.session.add(new_user)
        db.session.commit()
        
        response = logged_in_client.post(
            "/api/customers/is_admin",
            json={"toggle_admin_for": new_user.id}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["admin"] is True
        
        # Toggle back
        response = logged_in_client.post(
            "/api/customers/is_admin",
            json={"toggle_admin_for": new_user.id}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["admin"] is False