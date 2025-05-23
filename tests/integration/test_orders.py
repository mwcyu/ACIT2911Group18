import pytest
from datetime import datetime, timedelta
from flask import url_for
from models import Order, Product, ProductOrder
from db import db
from ..conftest import assert_flashed_message

class TestOrdersListing:
    """Test suite for orders listing page and its filtering/sorting features"""

    def test_view_orders_page(self, logged_in_client):
        """Test basic orders page load"""
        response = logged_in_client.get("/orders/")
        assert response.status_code == 200
        assert b"Orders" in response.data

    def test_sort_by_id(self, logged_in_client, test_user, db):
        """Test sorting orders by ID"""
        # Create two orders
        order1 = Order(customer=test_user, created=datetime.now())
        order2 = Order(customer=test_user, created=datetime.now())
        db.session.add_all([order1, order2])
        db.session.commit()

        # Test ascending sort
        response = logged_in_client.get("/orders/?sort=id&sort_order=asc")
        assert response.status_code == 200
        
        # Test descending sort
        response = logged_in_client.get("/orders/?sort=id&sort_order=desc")
        assert response.status_code == 200

    def test_sort_by_date(self, logged_in_client, test_user, db):
        """Test sorting orders by creation date"""
        # Create orders with different dates
        older_date = datetime.now() - timedelta(days=1)
        order1 = Order(customer=test_user, created=older_date)
        order2 = Order(customer=test_user, created=datetime.now())
        db.session.add_all([order1, order2])
        db.session.commit()

        response = logged_in_client.get("/orders/?sort=created&sort_order=desc")
        assert response.status_code == 200

    def test_filter_by_date_range(self, logged_in_client, test_user, db):
        """Test filtering orders by date range"""
        # Create orders in different date ranges
        old_date = datetime.now() - timedelta(days=5)
        recent_date = datetime.now() - timedelta(days=1)
        
        old_order = Order(customer=test_user, created=old_date)
        recent_order = Order(customer=test_user, created=recent_date)
        db.session.add_all([old_order, recent_order])
        db.session.commit()

        # Test date range filter
        start_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        response = logged_in_client.get(f"/orders/?date_filter=created_filter&start_date={start_date}&end_date={end_date}")
        assert response.status_code == 200

    def test_filter_completed_orders(self, logged_in_client, test_user, db):
        """Test filtering completed orders"""
        # Create completed and pending orders
        completed_order = Order(
            customer=test_user, 
            created=datetime.now() - timedelta(days=1),
            completed=datetime.now()
        )
        pending_order = Order(
            customer=test_user,
            created=datetime.now()
        )
        db.session.add_all([completed_order, pending_order])
        db.session.commit()

        # Test completed filter
        response = logged_in_client.get("/orders/?date_filter=completed_filter")
        assert response.status_code == 200


class TestSingleOrder:
    """Test suite for single order view"""

    def test_view_single_order(self, logged_in_client, test_user, test_product, db):
        """Test viewing a single order's details"""
        # Create an order with items
        order = Order(customer=test_user)
        db.session.add(order)
        db.session.flush()

        item = ProductOrder(product=test_product, quantity=2, order=order)
        db.session.add(item)
        db.session.commit()

        response = logged_in_client.get(f"/orders/{order.id}")
        assert response.status_code == 200
        assert test_product.name.encode() in response.data
        assert str(test_product.price).encode() in response.data


class TestOrderCompletion:
    """Test suite for order completion functionality"""

    def test_complete_order_success(self, logged_in_client, test_user, test_product, db):
        """Test successful order completion"""
        # Create order with available product
        order = Order(customer=test_user)
        db.session.add(order)
        db.session.flush()

        initial_stock = test_product.available
        order_quantity = 2
        item = ProductOrder(product=test_product, quantity=order_quantity, order=order)
        db.session.add(item)
        db.session.commit()

        # Complete the order
        response = logged_in_client.post(f"/orders/{order.id}/complete", follow_redirects=True)
        assert response.status_code == 200

        # Verify completion
        db.session.refresh(order)
        assert order.completed is not None
        assert test_product.available == initial_stock - order_quantity

    def test_complete_order_insufficient_stock(self, logged_in_client, test_user, test_product, db):
        """Test order completion with insufficient stock"""
        # Create order with quantity exceeding stock
        order = Order(customer=test_user)
        db.session.add(order)
        db.session.flush()

        test_product.available = 1
        excess_quantity = test_product.available + 1
        item = ProductOrder(product=test_product, quantity=excess_quantity, order=order)
        db.session.add(item)
        db.session.commit()

        # Attempt to complete order
        response = logged_in_client.post(f"/orders/{order.id}/complete", follow_redirects=True)
        assert response.status_code == 409  # Conflict status code

        # Verify order wasn't completed
        db.session.refresh(order)
        assert order.completed is None
        assert test_product.available == 1  # Stock should be unchanged
