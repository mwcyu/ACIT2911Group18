import pytest
from flask import session, url_for
from models import Order, ProductOrder
from ..conftest import assert_flashed_message
from datetime import datetime

class TestCartOperations:
    def test_view_empty_cart(self, logged_in_client):
        response = logged_in_client.get("/cart/")
        assert response.status_code == 200
        assert b"Your cart is empty" in response.data

    def test_add_product_to_cart(self, logged_in_client, test_product, test_user, db):
        response = logged_in_client.get(f"/cart/add/{test_product.id}", follow_redirects=True)
        assert response.status_code == 200
        assert_flashed_message(response, f"Added {test_product.name} to your cart.", "success")

        cart = db.session.execute(db.select(Order).where(Order.customer_id == test_user.id)).scalar()
        assert cart is not None
        assert len(cart.items) == 1
        assert cart.items[0].product_id == test_product.id
        assert cart.items[0].quantity == 1

    def test_update_cart_quantity(self, logged_in_client, test_product, test_user, db):
        logged_in_client.get(f"/cart/add/{test_product.id}")
        response = logged_in_client.post(
            f"/cart/update/{test_product.id}",
            data={"quantity": "3"},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert_flashed_message(response, "Quantity updated.", "success")

        cart = db.session.execute(db.select(Order).where(Order.customer_id == test_user.id)).scalar()
        assert cart.items[0].quantity == 3

    def test_remove_from_cart(self, logged_in_client, test_product, test_user, db):
        logged_in_client.get(f"/cart/add/{test_product.id}")
        response = logged_in_client.get(f"/cart/remove/{test_product.id}", follow_redirects=True)
        assert response.status_code == 200
        assert_flashed_message(response, "Item removed.", "info")

        cart = db.session.execute(db.select(Order).where(Order.customer_id == test_user.id)).scalar()
        assert len(cart.items) == 0

    def test_view_cart_with_items(self, logged_in_client, test_product):
        logged_in_client.get(f"/cart/add/{test_product.id}")
        response = logged_in_client.get("/cart/")
        assert response.status_code == 200
        assert test_product.name.encode() in response.data
        assert str(test_product.price).encode() in response.data


class TestCartCheckout:
    def test_successful_checkout(self, logged_in_client, test_product, test_user, db):
        logged_in_client.get(f"/cart/add/{test_product.id}")
        initial_stock = test_product.available

        response = logged_in_client.get("/cart/checkout", follow_redirects=True)
        assert response.status_code == 200
        assert_flashed_message(response, "Order completed successfully!", "success")

        order = db.session.execute(db.select(Order).where(Order.customer_id == test_user.id)).scalar()
        assert order.completed is not None
        db.session.refresh(test_product)
        assert test_product.available == initial_stock - 1

    def test_checkout_insufficient_stock(self, logged_in_client, test_product, test_user, db):
        logged_in_client.get(f"/cart/add/{test_product.id}")
        test_product.available = 0
        db.session.commit()

        response = logged_in_client.get("/cart/checkout", follow_redirects=True)
        assert response.status_code == 200
        assert_flashed_message(response, "One or more items exceed available stock.", "danger")


class TestCartGeneration:
    def test_generate_cart_page(self, logged_in_client):
        response = logged_in_client.get("/cart/generate")
        assert response.status_code == 200
        assert b"Smart Cart Generator" in response.data

    def test_generate_cart_with_budget(self, logged_in_client, test_product, test_user, db):
        response = logged_in_client.post("/cart/generate", data={"budget": "20.00"}, follow_redirects=True)
        assert response.status_code == 200
        assert_flashed_message(response, "Generated a cart under your budget.", "success")

        cart = db.session.execute(
            db.select(Order).where(Order.customer_id == test_user.id, Order.completed == None)
        ).scalar()
        assert cart is not None
        assert len(cart.items) > 0
        assert cart.estimate() <= 20.00

    def test_generate_cart_invalid_budget(self, logged_in_client):
        response = logged_in_client.post("/cart/generate", data={"budget": "-10.00"}, follow_redirects=True)
        assert response.status_code == 200
        assert_flashed_message(response, "Please enter a valid positive budget.", "danger")


class TestCartEdgeCases:
    def test_cart_with_out_of_stock_items(self, logged_in_client, test_product, test_user, db):
        test_product.available = 0
        db.session.commit()

        logged_in_client.get(f"/cart/add/{test_product.id}", follow_redirects=True)
        response = logged_in_client.get("/cart/checkout", follow_redirects=True)
        assert b"One or more items exceed available stock." in response.data

    def test_switch_order(self, logged_in_client, test_user, db):
        order = Order(customer=test_user)
        db.session.add(order)
        db.session.commit()

        res = logged_in_client.get(f"/cart/switch/{order.id}", follow_redirects=True)
        assert test_user.active_cart_id == order.id

        order2 = Order(customer=test_user)
        db.session.add(order2)
        db.session.commit()

        assert test_user.active_cart_id != order2.id

class TestCartRenameAndCoupon:
    def test_rename_cart(self, logged_in_client, test_user, db):
        order = Order(customer=test_user)
        db.session.add(order)
        db.session.commit()

        response = logged_in_client.post(
            f"/cart/rename/{order.id}",
            data={"new_name": "Weekly Groceries"},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert_flashed_message(response, "Cart name updated!", "success")
        db.session.refresh(order)
        assert order.name == "Weekly Groceries"

    def test_rename_cart_invalid_user(self, logged_in_client, test_user, db):
        another_order = Order(customer_id=9999)
        db.session.add(another_order)
        db.session.commit()

        response = logged_in_client.post(
            f"/cart/rename/{another_order.id}",
            data={"new_name": "Sneaky"},
            follow_redirects=True
        )
        assert response.status_code == 403

    def test_rename_cart_empty_name(self, logged_in_client, test_user, db):
        order = Order(customer=test_user)
        db.session.add(order)
        db.session.commit()

        response = logged_in_client.post(
            f"/cart/rename/{order.id}",
            data={"new_name": " "},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert_flashed_message(response, "Cart name cannot be empty.", "danger")

    def test_apply_valid_coupon(self, logged_in_client, test_user, test_product, db):
        from models import Coupon
        coupon = Coupon(code="SAVE10", discount_amount=10, is_percent=False, active=True, wheel_label="10%")
        test_user.coupons.append(coupon)
        db.session.add(coupon)
        db.session.commit()

        response = logged_in_client.post(
            "/cart/apply-coupon",
            data={"coupon_id": coupon.id},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert_flashed_message(response, f"Coupon {coupon.code} applied!", "success")

    def test_apply_invalid_coupon(self, logged_in_client, db):
        response = logged_in_client.post(
            "/cart/apply-coupon",
            data={"coupon_id": 9999},
            follow_redirects=True
        )
        assert response.status_code == 200
        assert_flashed_message(response, "Invalid or unavailable coupon.", "danger")
