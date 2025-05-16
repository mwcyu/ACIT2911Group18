from db import db
from models import Customer, Category, Product, Order, ProductOrder, Season, Coupon
from models.customerCoupon import customer_coupons
import random

from app import app, db

from random import randint
from datetime import datetime as dt
from datetime import timedelta

import sys
import csv

def create_tables():
    db.create_all()


def drop_tables():
    db.drop_all()


def str_to_bool(val):
    return str(val).strip().lower() == "true"


def csvReader(filename, klass):
    with open(filename, "r") as file:
        data = csv.DictReader(file)
        for item in data:
            if klass == Product:
                possible_category = db.session.execute(db.select(Category).where(Category.name == item["category"])).scalar()
                if not possible_category:
                    category_obj = Category(name=item["category"])
                    db.session.add(category_obj)
                else:
                    category_obj = possible_category
                possible_season = db.session.execute(db.select(Season).where(Season.name == item["season"])).scalar()
                if not possible_season:
                    season_obj = Season(name=item["season"])
                    db.session.add(season_obj)
                else:
                    season_obj = possible_season
                item["price"] = float(item["price"])
                item["available"] = int(item["available"])
                item["in_season"] = str_to_bool(item.get("in_season", False))
                item["category"] = category_obj
                item["season"] = season_obj
                db.session.add(klass(**item))
            elif klass == Customer:
                # Hash the password before creating the Customer
                password = item.pop("password", None)
                customer = klass(**item)
                if password:
                    customer.set_password(password)
                db.session.add(customer)
            elif klass == Coupon:
                # Convert types for Coupon fields
                item["minimum_purchase"] = float(item["minimum_purchase"]) if item["minimum_purchase"] else 0.0
                item["discount_amount"] = float(item["discount_amount"])
                item["is_percent"] = str_to_bool(item["is_percent"])
                item["active"] = str_to_bool(item["active"])
                db.session.add(klass(**item))
            elif klass == customer_coupons:
                item["customer_id"] = int(item["customer_id"])
                item["coupon_id"] = int(item["coupon_id"])
                db.session.add(klass(**item))
            else:
                db.session.add(klass(**item))
        db.session.commit()



def make_orders():
    for _ in range(50):
        random_customer = db.session.execute(db.select(Customer).order_by(db.func.random())).scalar()
        random_date = dt.now() - timedelta(days=randint(1, 3), hours=randint(0, 15), minutes=randint(0, 30))
        current_order = Order(customer=random_customer, created=random_date)
        db.session.add(current_order)
        num_product_orders = random.randint(4, 6)
        random_prods = db.session.execute(db.select(Product).order_by(db.func.random()).limit(num_product_orders)).scalars()
        for prod in random_prods:
            quantity = random.randint(4, 6)
            db.session.add(ProductOrder(product=prod, quantity=quantity, order=current_order))
        
    db.session.commit()

# This is for making fake completed orders
def make_completed_orders():
    for _ in range(50):
        random_customer = db.session.execute(
            db.select(Customer).order_by(db.func.random())
        ).scalar()

        # Generate a random creation date up to 40 days ago
        created_date = dt.now() - timedelta(
            days=randint(1, 40), hours=randint(0, 15), minutes=randint(0, 59)
        )

        # 70% chance of being completed
        is_completed = random.random() < 0.7

        # If completed, set a completion time 1–8 hours after creation
        completed_date = None
        if is_completed:
            completed_date = created_date + timedelta(
                hours=randint(1, 8), minutes=randint(0, 59)
            )

        # Create the order
        order = Order(
            customer=random_customer,
            created=created_date,
            completed=completed_date
        )
        db.session.add(order)
        db.session.flush()  # ensure order.id is available

        # Add random products
        num_items = randint(4, 6)
        products = db.session.execute(
            db.select(Product).order_by(db.func.random()).limit(num_items)
        ).scalars()

        for product in products:
            quantity = randint(1, 5)
            db.session.add(ProductOrder(product=product, quantity=quantity, order=order))

        # If completed, estimate total and reduce inventory
        if is_completed:
            order.amount = order.estimate()
            for item in order.items:
                item.product.available = max(0, item.product.available - item.quantity)

    db.session.commit()


    
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Manage the database.")
    parser.add_argument("command", choices=["create", "drop", "import", "orders", "completed_orders", "reset"], help="Action to perform")
    args = parser.parse_args()

    with app.app_context():
        if args.command == "create":
            create_tables()
        elif args.command == "drop":
            drop_tables()
        elif args.command == "import":
            csvReader("products.csv", Product)
            csvReader("customers.csv", Customer)
            csvReader("coupons.csv", Coupon)
        elif args.command == "orders":
            make_orders()
        elif args.command == "completed_orders":
            make_completed_orders()
        elif args.command == "reset":
            drop_tables()
            create_tables()
            csvReader("products.csv", Product)
            csvReader("customers.csv", Customer)
            csvReader("coupons.csv", Coupon)
            make_orders()
            make_completed_orders()