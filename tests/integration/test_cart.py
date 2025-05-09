# tests/test_cart.py
import random
import pytest
from models import Product, ProductOrder, Order
from bs4 import BeautifulSoup
from flask import url_for


def test_add_to_cart(logged_in_client, test_product, test_user, db):
    """Test adding a product to cart"""
    response = logged_in_client.get(f"/cart/add/{test_product.id}", follow_redirects=True)
    assert response.status_code == 200
    assert f"Added {test_product.name} to your cart.".encode() in response.data
    
    # Verify cart was created and product added
    cart = db.session.execute(db.select(Order).where(Order.customer_id == test_user.id)).scalar()
    assert cart is not None
    assert len(cart.items) == 1
    assert cart.items[0].product_id == test_product.id
    assert cart.items[0].quantity == 1


def test_view_cart(logged_in_client, test_product, test_user, db):
    """Test viewing cart contents"""
    # Add item to cart first
    logged_in_client.get(f"/cart/add/{test_product.id}")
    
    response = logged_in_client.get("/cart/")
    assert response.status_code == 200
    assert test_product.name.encode() in response.data
    assert str(test_product.price).encode() in response.data


def test_update_cart_quantity(logged_in_client, test_product, test_user, db):
    """Test updating product quantity in cart"""
    # Add item to cart first
    logged_in_client.get(f"/cart/add/{test_product.id}")
    
    # Update quantity
    response = logged_in_client.post(
        f"/cart/update/{test_product.id}",
        data={"quantity": "3"},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Quantity updated." in response.data
    
    # Verify quantity was updated
    cart = db.session.execute(db.select(Order).where(Order.customer_id == test_user.id)).scalar()
    assert cart.items[0].quantity == 3


def test_remove_from_cart(logged_in_client, test_product, test_user, db):
    """Test removing an item from cart"""
    # Add item to cart first
    logged_in_client.get(f"/cart/add/{test_product.id}")
    
    # Remove item
    response = logged_in_client.get(f"/cart/remove/{test_product.id}", follow_redirects=True)
    assert response.status_code == 200
    assert b"Item removed." in response.data
    
    # Verify item was removed
    cart = db.session.execute(db.select(Order).where(Order.customer_id == test_user.id)).scalar()
    assert len(cart.items) == 0


def test_checkout_cart(logged_in_client, test_product, test_user, db):
    """Test checking out cart"""
    # Add item to cart first
    logged_in_client.get(f"/cart/add/{test_product.id}")
    
    initial_inventory = test_product.available
    
    # Checkout
    response = logged_in_client.get("/cart/checkout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Order completed successfully!" in response.data
    
    # Verify order was completed and inventory reduced
    order = db.session.execute(
        db.select(Order).where(Order.customer_id == test_user.id)
    ).scalar()
    assert order.completed is not None
    assert float(order.amount) == float(test_product.price)  # Convert Decimal to float for comparison
    
    # Refresh product from db
    db.session.refresh(test_product)
    assert test_product.available == initial_inventory - 1


def test_generate_cart(logged_in_client, test_product, test_user, db):
    """Test generating a cart with budget"""
    response = logged_in_client.post(
        "/cart/generate",
        data={"budget": "20.00"},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Generated a cart under your budget." in response.data
    
    # Verify cart was created with items
    cart = db.session.execute(
        db.select(Order).where(
            Order.customer_id == test_user.id,
            Order.completed == None
        )
    ).scalar()
    assert cart is not None
    assert len(cart.items) > 0
    assert cart.estimate() <= 20.00


def test_cart_with_out_of_stock_items(logged_in_client, test_product, test_user, db):
    """Test checkout fails with out of stock items"""
    # Set product as out of stock
    test_product.available = 0
    db.session.commit()
    
    # Try to add to cart
    response = logged_in_client.get(f"/cart/add/{test_product.id}", follow_redirects=True)
    assert response.status_code == 200
    
    # Try to checkout
    response = logged_in_client.get("/cart/checkout", follow_redirects=True)
    assert b"One or more items exceed available stock." in response.data


def test_switch_order(logged_in_client, test_user,db):
    order = Order(customer=test_user)
    db.session.add(order)
    db.session.commit()

    res = logged_in_client.get(f"/cart/switch/{order.id}", follow_redirects=True)
    assert test_user.active_cart_id == order.id
    
    order2 = Order(customer=test_user)
    db.session.add(order2)
    db.session.commit()
    
    assert test_user.active_cart_id != order2.id