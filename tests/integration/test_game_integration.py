import pytest
from flask import url_for
from models import Coupon
from db import db
import json

class TestGameIntegration:
    """Integration tests for the game module (slot machine, wheel, etc.)"""

    def test_slot_machine_page_loads(self, logged_in_client):
        """Test that slot machine page loads correctly"""
        response = logged_in_client.get('/game/slot-machine')
        
        # Check success and basic structure
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert 'slot-machine' in html.lower() or 'slot machine' in html.lower()
        assert 'spin' in html.lower()
    
    def test_slot_machine_with_active_coupons(self, logged_in_client, db):
        """Test that active coupons are displayed on the slot machine page"""
        # Create multiple active coupons
        coupons = [
            Coupon(code="SPIN10", description="10% off", discount_amount=10, is_percent=True, active=True),
            Coupon(code="SPIN20", description="20% off", discount_amount=20, is_percent=True, active=True),
            Coupon(code="SPIN30", description="$30 off", discount_amount=30, is_percent=False, active=True)
        ]
        
        for coupon in coupons:
            db.session.add(coupon)
        db.session.commit()
        
        # Access the page
        response = logged_in_client.get('/game/slot-machine')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        
        # Check all coupons are present
        for coupon in coupons:
            assert coupon.code in html
            assert coupon.description in html
            assert str(coupon.discount_amount) in html
    
    def test_slot_machine_inactive_coupons_excluded(self, logged_in_client, db):
        """Test that inactive coupons don't appear on the slot machine page"""
        # Create active and inactive coupons
        active_coupon = Coupon(code="ACTIVE", description="Active coupon", discount_amount=10, is_percent=True, active=True)
        inactive_coupon = Coupon(code="INACTIVE", description="Inactive coupon", discount_amount=20, is_percent=True, active=False)
        
        db.session.add(active_coupon)
        db.session.add(inactive_coupon)
        db.session.commit()
        
        # Access the page
        response = logged_in_client.get('/game/slot-machine')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        
        # Check only active coupon is present
        assert active_coupon.code in html
        assert inactive_coupon.code not in html
    
    def test_slot_machine_spin_api(self, logged_in_client):
        """Test the slot machine spin API endpoint"""
        # Create test coupon
        coupon = Coupon(code="API10", description="API Test Coupon", discount_amount=10, is_percent=True, active=True)
        db.session.add(coupon)
        db.session.commit()
        
        # Call the spin API
        response = logged_in_client.post(
            '/game/slot-machine', 
            json={"action": "spin"},
            content_type="application/json"
        )
        
        # Check response format
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "success" in data
        assert data["success"] is True
        assert "is_win" in data  # Could be True or False depending on random
        
    def test_slot_machine_claim_coupon_workflow(self, logged_in_client, test_user, db):
        """Test the full workflow of claiming a coupon from the slot machine"""
        # Create test coupon
        coupon = Coupon(code="WORKFLOW", description="Workflow Test", discount_amount=25, is_percent=True, active=True)
        db.session.add(coupon)
        db.session.commit()
        
        # Submit claim form
        response = logged_in_client.post(
            '/game/slot-machine',
            data={"coupon_code": "WORKFLOW"},
            follow_redirects=True
        )
        
        # Should add coupon to user and redirect
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert "added to your account" in html
        
        # Verify coupon was added to user
        db.session.refresh(test_user)
        assert any(c.code == "WORKFLOW" for c in test_user.coupons)
    
    def test_no_prize_option_when_no_coupons(self, logged_in_client, db):
        """Test that 'no prize' option is shown when no active coupons exist"""
        # Delete all coupons first
        db.session.query(Coupon).delete()
        db.session.commit()
        
        # Access the slot machine page
        response = logged_in_client.get('/game/slot-machine')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        
        # Should show 'no prize' option
        assert "NO_PRIZE" in html or "No prize" in html or "No prizes available" in html
    
    def test_authentication_required(self, client):
        """Test that slot machine requires authentication"""
        # Try to access without being logged in
        response = client.get('/game/slot-machine', follow_redirects=True)
        
        # Should redirect to login page
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert "login" in html.lower()
        assert "please log in to access this page" in html.lower() or "please login" in html.lower()
