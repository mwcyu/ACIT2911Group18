# tests/test_cart.py
import random
from db import db
from models import Product, ProductOrder, Order
from bs4 import BeautifulSoup

def add_product(name, category_id, price=2.50, available=10):
    product = Product(name=name, price=price, available=available,
                      category_id=category_id, seasonal=True, in_season=True)
    db.session.add(product)
    db.session.commit()
    return product


def test_add_to_cart(logged_in_client, test_user, test_category):
    product = add_product("Apple", test_category.id)

    res = logged_in_client.get(f"/cart/add/{product.id}", follow_redirects=True)
    print(res.data.decode())  # Helpful for debugging output

    # Check the order was created and is still pending (not completed)
    stmt = db.select(Order).where(Order.customer_id == test_user.id, Order.completed == None)
    order = db.session.execute(stmt).scalar_one_or_none()

    assert order is not None, "Pending order should exist"
    assert order.customer_id == test_user.id

    # Check that the product was added to the order
    item = next((i for i in order.items if i.product_id == product.id), None)
    assert item is not None, "Item was not added to order"
    assert item.quantity == 1


def test_update_cart_item(logged_in_client, test_user, test_category):
    product = add_product("Banana", test_category.id)
    order = Order(customer=test_user)
    db.session.add(order)
    db.session.flush()
    item = ProductOrder(product_id=product.id, quantity=1, order_id=order.id)
    db.session.add(item)
    db.session.commit()

    res = logged_in_client.post(f"/cart/update/{product.id}", data={"quantity": 3}, follow_redirects=True)
    
    # finds the exact entry and verifies it
    assert db.session.get(ProductOrder, (product.id, order.id)).quantity == 3


def test_remove_cart_item(logged_in_client, test_user, test_category):
    product = add_product("Grapes", test_category.id)
    order = Order(customer=test_user)
    db.session.add(order)
    db.session.flush()
    item = ProductOrder(product_id=product.id, quantity=1, order_id=order.id)
    db.session.add(item)
    db.session.commit()
    
    # Test that it actually added it, with 1 quantity
    assert db.session.get(ProductOrder, (product.id, order.id)).quantity == 1

    res = logged_in_client.get(f"/cart/remove/{product.id}", follow_redirects=True)
    
    # Test to see if it is gone
    assert db.session.get(ProductOrder, (product.id, order.id)) == None

def test_generate_cart_random_quantity(logged_in_client, test_user, test_category):
    # Add 5 seasonal, in-season products with random prices
    for i in range(5):
        add_product(
            name=f"Seasonal{i}",
            category_id=test_category.id,
            price=random.uniform(1.0, 3.0),
            available=10
        )

    test_budget = 30.0

    # Generate cart under budget
    response = logged_in_client.post("/cart/generate", data={"budget": test_budget}, follow_redirects=True)

    # Get the pending order for the test user
    stmt = db.select(Order).where(Order.customer_id == test_user.id, Order.completed == None)
    order = db.session.execute(stmt).scalar_one_or_none()
    
    print(order.to_json())
    
    # Testing to see if it actually made an order
    assert order != None
    
    total = order.estimate()
    
    # Testing if the cart total is less than the test_budget
    assert total <= test_budget
    


def test_switch_order(logged_in_client, test_user):
    order = Order(customer=test_user)
    db.session.add(order)
    db.session.commit()

    res = logged_in_client.get(f"/cart/switch/{order.id}", follow_redirects=True)
    assert test_user.active_cart_id == order.id
    
    order2 = Order(customer=test_user)
    db.session.add(order2)
    db.session.commit()
    
    assert test_user.active_cart_id != order2.id