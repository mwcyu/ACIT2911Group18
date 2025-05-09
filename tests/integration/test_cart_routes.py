"""Integration tests for cart functionality"""
import pytest
from flask import session
from models import Order, ProductOrder
from ..conftest import assert_flashed_message

class TestCartOperations:
    def test_view_empty_cart(self, logged_in_client):
        """Test viewing an empty cart"""
        response = logged_in_client.get("/cart/")
        assert response.status_code == 200
        assert b"Your cart is empty" in response.data
        
    def test_add_product_to_cart(self, logged_in_client, test_product):
        """Test adding a product to cart"""
        response = logged_in_client.get(
            f"/cart/add/{test_product.id}",
            follow_redirects=True
        )
        assert response.status_code == 200
        assert_flashed_message(
            response,
            f"Added {test_product.name} to your cart.",
            "success"
        )
        
        # Verify cart contents
        cart_response = logged_in_client.get("/cart/")
        assert test_product.name.encode() in cart_response.data
        assert str(test_product.price).encode() in cart_response.data

    def test_update_cart_quantity(self, logged_in_client, test_product, test_user, db):
        """Test updating product quantity in cart"""
        # First add item to cart
        logged_in_client.get(f"/cart/add/{test_product.id}")
        
        # Update quantity
        response = logged_in_client.post(
            f"/cart/update/{test_product.id}",
            data={"quantity": "3"},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert_flashed_message(response, "Quantity updated.", "success")
        
        # Verify quantity in database
        order = db.session.execute(
            db.select(Order).where(Order.customer_id == test_user.id)
        ).scalar()
        assert order.items[0].quantity == 3

    def test_remove_from_cart(self, logged_in_client, test_product, test_user, db):
        """Test removing an item from cart"""
        # Add item first
        logged_in_client.get(f"/cart/add/{test_product.id}")
        
        # Remove item
        response = logged_in_client.get(
            f"/cart/remove/{test_product.id}",
            follow_redirects=True
        )
        assert response.status_code == 200
        assert_flashed_message(response, "Item removed.", "info")
        
        # Verify item was removed
        order = db.session.execute(
            db.select(Order).where(Order.customer_id == test_user.id)
        ).scalar()
        assert len(order.items) == 0

class TestCartCheckout:
    def test_successful_checkout(self, logged_in_client, test_product, test_user, db):
        """Test successful cart checkout"""
        # Add item to cart
        logged_in_client.get(f"/cart/add/{test_product.id}")
        initial_stock = test_product.available
        
        # Checkout
        response = logged_in_client.get("/cart/checkout", follow_redirects=True)
        assert response.status_code == 200
        assert_flashed_message(response, "Order completed successfully!", "success")
        
        # Verify order status and inventory
        order = db.session.execute(
            db.select(Order).where(Order.customer_id == test_user.id)
        ).scalar()
        assert order.completed is not None
        db.session.refresh(test_product)
        assert test_product.available == initial_stock - 1

    def test_checkout_insufficient_stock(self, logged_in_client, test_product, db):
        """Test checkout with insufficient stock"""
        # Add item to cart
        logged_in_client.get(f"/cart/add/{test_product.id}")
        
        # Set stock to 0
        test_product.available = 0
        db.session.commit()
        
        # Try to checkout
        response = logged_in_client.get("/cart/checkout", follow_redirects=True)
        assert response.status_code == 200
        assert_flashed_message(
            response,
            "One or more items exceed available stock.",
            "danger"
        )

class TestCartGeneration:
    def test_generate_cart_page(self, logged_in_client):
        """Test cart generation page loads"""
        response = logged_in_client.get("/cart/generate")
        assert response.status_code == 200
        assert b"Smart Cart Generator" in response.data

    def test_generate_cart_with_budget(self, logged_in_client, test_product):
        """Test generating a cart with budget"""
        response = logged_in_client.post(
            "/cart/generate",
            data={"budget": "50.00"},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert_flashed_message(
            response,
            "Generated a cart under your budget.",
            "success"
        )

    def test_generate_cart_invalid_budget(self, logged_in_client):
        """Test generating a cart with invalid budget"""
        response = logged_in_client.post(
            "/cart/generate",
            data={"budget": "-10.00"},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert_flashed_message(
            response,
            "Please enter a valid positive budget.",
            "danger"
        )