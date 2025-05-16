import sys
import csv
import random
from datetime import datetime as dt, timedelta
from db import db
from models import Customer, Category, Product, Order, ProductOrder, Season, Coupon
from models.customerCoupon import customer_coupons
from app import create_app

app = create_app()

def create_tables():
    db.create_all()
    print("✅ Tables created.")

def drop_tables():
    db.drop_all()
    print("⚠️ Tables dropped.")

def str_to_bool(val):
    return str(val).strip().lower() == "true"

def csvReader(filename, klass):
    print(f"📄 Importing: {filename}")
    with open(filename, "r") as file:
        data = csv.DictReader(file)
        for item in data:
            if klass == Product:
                # Category
                category_obj = (
                    db.session.execute(
                        db.select(Category).where(Category.name == item["category"])
                    ).scalar()
                    or Category(name=item["category"])
                )
                db.session.add(category_obj)

                # Season
                season_obj = (
                    db.session.execute(
                        db.select(Season).where(Season.name == item["season"])
                    ).scalar()
                    or Season(name=item["season"])
                )
                db.session.add(season_obj)

                item["price"] = float(item["price"])
                item["available"] = int(item["available"])
                item["in_season"] = str_to_bool(item.get("in_season", False))
                item["category"] = category_obj
                item["season"] = season_obj
                db.session.add(klass(**item))

            elif klass == Customer:
                password = item.pop("password", None)
                customer = klass(**item)
                if password:
                    customer.set_password(password)
                db.session.add(customer)

            elif klass == Coupon:
                item["minimum_purchase"] = float(item["minimum_purchase"] or 0)
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
    print(f"✅ {filename} imported.")

def make_orders():
    for _ in range(50):
        customer = db.session.execute(db.select(Customer).order_by(db.func.random())).scalar()
        date = dt.now() - timedelta(days=random.randint(1, 3), hours=random.randint(0, 15))
        order = Order(customer=customer, created=date)
        db.session.add(order)

        prods = db.session.execute(
            db.select(Product).order_by(db.func.random()).limit(random.randint(4, 6))
        ).scalars()
        for prod in prods:
            db.session.add(ProductOrder(product=prod, quantity=random.randint(4, 6), order=order))

    db.session.commit()
    print("🛒 Random orders created.")

def make_completed_orders():
    for _ in range(50):
        customer = db.session.execute(db.select(Customer).order_by(db.func.random())).scalar()
        created = dt.now() - timedelta(days=random.randint(1, 40), hours=random.randint(0, 15))
        completed = created + timedelta(hours=random.randint(1, 8)) if random.random() < 0.7 else None

        order = Order(customer=customer, created=created, completed=completed)
        db.session.add(order)
        db.session.flush()

        items = db.session.execute(
            db.select(Product).order_by(db.func.random()).limit(random.randint(4, 6))
        ).scalars()

        for item in items:
            qty = random.randint(1, 5)
            db.session.add(ProductOrder(product=item, quantity=qty, order=order))
            if completed:
                item.available = max(0, item.available - qty)

        if completed:
            order.amount = order.estimate()

    db.session.commit()
    print("✅ Completed orders created.")

def seed_data():
    csvReader("products.csv", Product)
    csvReader("customers.csv", Customer)
    csvReader("coupons.csv", Coupon)
    make_orders()
    make_completed_orders()

if __name__ == "__main__":
    with app.app_context():
        if len(sys.argv) < 2:
            print("❌ Usage: python manage.py [create|drop|seed|reset]")
            sys.exit(1)

        command = sys.argv[1]

        if command == "create":
            create_tables()
        elif command == "drop":
            drop_tables()
        elif command == "seed":
            seed_data()
        elif command == "reset":
            drop_tables()
            create_tables()
            seed_data()
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: create, drop, seed, reset")
