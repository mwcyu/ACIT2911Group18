import pytest
from unittest.mock import patch, MagicMock
from flask import url_for
from models import Coupon
from db import db

class TestGameRoutes:
    """Test suite for game-related routes (slot machine, etc.)"""

    def test_slot_machine_get(self, logged_in_client, test_user, db):
        """Test GET request to slot machine page"""
        # Create a test coupon
        coupon = Coupon(
            code="TEST10", 
            description="10% off", 
            discount_amount=10, 
            is_percent=True,
            active=True,
            wheel_label="10%"
        )
        db.session.add(coupon)
        db.session.commit()

        # Access the slot machine page
        response = logged_in_client.get('/game/slot-machine')
        
        # Check the response
        assert response.status_code == 200
        assert b'slot_machine.html' in response.data or b'slot-machine' in response.data
        
        # Check that coupon data is included
        assert b'TEST10' in response.data
        assert b'10% off' in response.data

    def test_slot_machine_get_no_coupons(self, logged_in_client):
        """Test slot machine page with no coupons available"""
        # Access the slot machine page
        response = logged_in_client.get('/game/slot-machine')
        
        # Check the response
        assert response.status_code == 200
        
        # Should show "no prize" option
        assert b'No prizes available' in response.data

    @patch('random.random')
    def test_slot_machine_spin_win(self, mock_random, logged_in_client, test_user, db):
        """Test JSON API for slot machine spin with winning outcome"""
        # Mock random to ensure a win (value < 0.3)
        mock_random.return_value = 0.1
        
        # Create a test coupon
        coupon = Coupon(
            code="WIN50", 
            description="50% off", 
            discount_amount=50, 
            is_percent=True,
            active=True,
            wheel_label="50%"
        )
        db.session.add(coupon)
        db.session.commit()

        # Send spin request
        response = logged_in_client.post(
            '/game/slot-machine',
            json={'action': 'spin'},
            content_type='application/json'
        )
        
        # Check response
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        assert json_data['is_win'] is True
        assert json_data['coupon']['code'] == 'WIN50'
        assert json_data['coupon']['description'] == '50% off'

    @patch('random.random')
    def test_slot_machine_spin_lose(self, mock_random, logged_in_client):
        """Test JSON API for slot machine spin with losing outcome"""
        # Mock random to ensure a loss (value > 0.3)
        mock_random.return_value = 0.5
        
        # Send spin request
        response = logged_in_client.post(
            '/game/slot-machine',
            json={'action': 'spin'},
            content_type='application/json'
        )
        
        # Check response
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        assert json_data['is_win'] is False
        assert 'coupon' not in json_data

    def test_slot_machine_claim_new_coupon(self, logged_in_client, test_user, db):
        """Test claiming a new coupon through the form submission"""
        # Create a test coupon
        coupon = Coupon(
            code="CLAIM25", 
            description="25% off", 
            discount_amount=25, 
            is_percent=True,
            active=True,
            wheel_label="25%"
        )
        db.session.add(coupon)
        db.session.commit()

        # Submit claim form
        response = logged_in_client.post(
            '/game/slot-machine',
            data={'coupon_code': 'CLAIM25'},
            follow_redirects=True
        )
        
        # Check response and flash message
        assert response.status_code == 200
        assert b'added to your account' in response.data
        
        # Check that user now has the coupon
        user = db.session.get(test_user.__class__, test_user.id)
        assert coupon in user.coupons

    def test_slot_machine_claim_existing_coupon(self, logged_in_client, test_user, db):
        """Test trying to claim a coupon the user already has"""
        # Create a test coupon and assign to user
        coupon = Coupon(
            code="ALREADY50", 
            description="50% off", 
            discount_amount=50, 
            is_percent=True,
            active=True,
            wheel_label="50%"
        )
        db.session.add(coupon)
        test_user.coupons.append(coupon)
        db.session.commit()

        # Submit claim form
        response = logged_in_client.post(
            '/game/slot-machine',
            data={'coupon_code': 'ALREADY50'},
            follow_redirects=True
        )
        
        # Check response and flash message
        assert response.status_code == 200
        assert b'already have this coupon' in response.data

    def test_slot_machine_claim_invalid_coupon(self, logged_in_client):
        """Test trying to claim a coupon that doesn't exist"""
        # Submit claim form with invalid code
        response = logged_in_client.post(
            '/game/slot-machine',
            data={'coupon_code': 'INVALID'},
            follow_redirects=True
        )
        
        # Check response and flash message
        assert response.status_code == 200
        assert b'Invalid coupon code' in response.data

    def test_slot_machine_invalid_action(self, logged_in_client):
        """Test JSON API with invalid action parameter"""
        # Send request with invalid action
        response = logged_in_client.post(
            '/game/slot-machine',
            json={'action': 'invalid'},
            content_type='application/json'
        )
        
        # Check response
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data['success'] is False
        assert 'error' in json_data

    def test_slot_machine_exception_handling(self, logged_in_client, monkeypatch):
        """Test exception handling in JSON API"""
        # Mock db.select to raise an exception
        def mock_select(*args, **kwargs):
            raise Exception("Database error")
        
        monkeypatch.setattr(db, 'select', mock_select)
        
        # Send spin request
        response = logged_in_client.post(
            '/game/slot-machine',
            json={'action': 'spin'},
            content_type='application/json'
        )
        
        # Check response
        assert response.status_code == 500
        json_data = response.get_json()
        assert json_data['success'] is False
        assert 'error' in json_data
