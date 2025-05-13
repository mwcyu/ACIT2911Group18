import pytest
from decimal import Decimal
from models import Order, ProductOrder, Product
from db import db


def test_estimate_empty_order(db, test_user):
    """Test estimate returns 0 for empty order"""
    order = Order(customer=test_user)
    db.session.add(order)
    db.session.commit()
    
    assert order.estimate() == Decimal('0')


def test_estimate_with_items(db, test_user, test_product):
    """Test estimate calculation with items"""
    order = Order(customer=test_user)
    db.session.add(order)
    
    # Add two items to the order
    item1 = ProductOrder(product=test_product, quantity=2, order=order)
    db.session.add(item1)
    db.session.commit()
    
    # Expected total: 2 * 9.99 = 19.98
    assert order.estimate() == float(19.98)


def test_estimate_with_multiple_items(db, test_user, test_product):
    """Test estimate with multiple different items"""
    order = Order(customer=test_user)
    db.session.add(order)
    
    # Create second product
    product2 = Product(
        name="Second Product",
        price=5.99,
        available=5,
        category=test_product.category
    )
    db.session.add(product2)
    
    # Add items to order
    item1 = ProductOrder(product=test_product, quantity=2, order=order)  # 2 * 9.99
    item2 = ProductOrder(product=product2, quantity=3, order=order)      # 3 * 5.99
    db.session.add_all([item1, item2])
    db.session.commit()
    
    # Expected: (2 * 9.99) + (3 * 5.99) = 19.98 + 17.97 = 37.95
    assert order.estimate() == float(37.95)


def test_complete_success(db, test_user, test_product):
    """Test successful order completion"""
    order = Order(customer=test_user)
    db.session.add(order)
    
    initial_inventory = test_product.available
    order_quantity = 2
    
    item = ProductOrder(product=test_product, quantity=order_quantity, order=order)
    db.session.add(item)
    db.session.commit()
    
    # Complete the order
    order.complete()
    db.session.commit()
    
    assert order.completed is not None
    assert order.amount == order.estimate()
    assert test_product.available == initial_inventory - order_quantity
    assert test_user.active_cart_id != order.id


def test_complete_insufficient_inventory(db, test_user, test_product):
    """Test order completion fails with insufficient inventory"""
    order = Order(customer=test_user)
    db.session.add(order)
    
    # Try to order more than available
    excess_quantity = test_product.available + 1
    item = ProductOrder(product=test_product, quantity=excess_quantity, order=order)
    db.session.add(item)
    db.session.commit()
    
    # Attempt to complete should raise ValueError
    with pytest.raises(ValueError):
        order.complete()
    
    # Verify no changes were made
    assert order.completed is None
    assert test_product.available == test_product.available  # Inventory unchanged
    assert order.amount is None


def test_complete_active_cart(db, test_user, test_product):
    """Test completion clears active cart reference"""
    order = Order(customer=test_user)
    db.session.add(order)
    db.session.commit()
    
    # Set as active cart
    test_user.active_cart_id = order.id
    db.session.commit()
    
    # Add item and complete
    item = ProductOrder(product=test_product, quantity=1, order=order)
    db.session.add(item)
    db.session.commit()
    
    order.complete()
    db.session.commit()
    
    assert test_user.active_cart_id is None