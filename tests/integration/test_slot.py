import pytest
import json
from unittest.mock import patch
from models import Coupon, Customer
from db import db

class TestSlotMachine:
    """Tests focused on the slot machine game functionality"""
    
    def test_slot_machine_symbols_assignment(self, logged_in_client, db):
        """Test that symbols are correctly assigned to coupons"""
        # Create coupons
        coupons = [
            Coupon(code=f"SYMBOL{i}", description=f"Symbol Test {i}", 
                   discount_amount=i*5, is_percent=True, active=True, wheel_label="symbol")
            for i in range(1, 10)
        ]
        
        for coupon in coupons:
            db.session.add(coupon)
        db.session.commit()
        
        # Get slot machine page
        response = logged_in_client.get('/game/slot-machine')
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        
        # Check each coupon has a symbol (bi-* class)
        for i in range(1, 10):
            assert f"SYMBOL{i}" in html
            assert "bi-" in html  # Bootstrap icon classes should be present
    
    @patch('random.random')
    @patch('random.choice')
    def test_slot_machine_win_response(self, mock_choice, mock_random, logged_in_client, db):
        """Test the slot machine win response format"""
        # Create test coupon
        coupon = Coupon(code="WIN-TEST", description="Win Test Coupon", 
                        discount_amount=50, is_percent=True, active=True, wheel_label="win")
        db.session.add(coupon)
        db.session.commit()
        
        # Force a win result
        mock_random.return_value = 0.1  # Less than 0.3 for a win
        mock_choice.return_value = coupon
        
        # Call spin API
        response = logged_in_client.post(
            '/game/slot-machine',
            json={"action": "spin"},
            content_type="application/json"
        )
        
        # Verify response structure for a win
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["is_win"] is True
        assert "coupon" in data
        assert data["coupon"]["code"] == "WIN-TEST"
        assert data["coupon"]["description"] == "Win Test Coupon"
        assert "icon" in data["coupon"]  # Should have an icon assigned
    
    @patch('random.random')
    def test_slot_machine_lose_response(self, mock_random, logged_in_client, db):
        """Test the slot machine lose response format"""
        # Create test coupon to ensure there are active coupons
        coupon = Coupon(code="LOSE-TEST", description="Lose Test Coupon", 
                        discount_amount=10, is_percent=True, active=True, wheel_label="lose")
        db.session.add(coupon)
        db.session.commit()
        
        # Force a lose result
        mock_random.return_value = 0.9  # Greater than 0.3 for a loss
        
        # Call spin API
        response = logged_in_client.post(
            '/game/slot-machine',
            json={"action": "spin"},
            content_type="application/json"
        )
        
        # Verify response structure for a loss
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["is_win"] is False
        assert "coupon" not in data
    
    def test_coupon_already_owned(self, logged_in_client, test_user, db):
        """Test claiming a coupon the user already owns"""
        # Create coupon and add to user
        coupon = Coupon(code="DUPE-TEST", description="Already Owned Coupon", 
                        discount_amount=15, is_percent=True, active=True, wheel_label="dupe")
        db.session.add(coupon)
        test_user.coupons.append(coupon)
        db.session.commit()
        
        # Try to claim the same coupon
        response = logged_in_client.post(
            '/game/slot-machine',
            data={"coupon_code": "DUPE-TEST"},
            follow_redirects=True
        )
        
        # Check response
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert "already have this coupon" in html
        
        # Verify user still has only one instance of the coupon
        db.session.refresh(test_user)
        assert len([c for c in test_user.coupons if c.code == "DUPE-TEST"]) == 1
    
    def test_claiming_inactive_coupon(self, logged_in_client, db):
        """Test attempting to claim an inactive coupon"""
        # Create inactive coupon
        coupon = Coupon(code="INACTIVE-TEST", description="Inactive Coupon", 
                        discount_amount=20, is_percent=True, active=False, wheel_label="inactive")
        db.session.add(coupon)
        db.session.commit()
        
        # Try to claim the inactive coupon
        response = logged_in_client.post(
            '/game/slot-machine',
            data={"coupon_code": "INACTIVE-TEST"},
            follow_redirects=True
        )
        
        # Check response
        assert response.status_code == 200
        html = response.data.decode('utf-8')
        assert "Invalid coupon code" in html