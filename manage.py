from db import db
from models import Customer, Category, Product, Order, ProductOrder
import random

from app import app

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
                    
                item["price"] = float(item["price"])
                item["available"] = int(item["available"])
                item["seasonal"] = str_to_bool(item.get("seasonal", False))
                item["in_season"] = str_to_bool(item.get("in_season", False))
                item["category"] = category_obj
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
        random_customer = db.session.execute(db.select(Customer).order_by(db.func.random())).scalar()
        random_date = dt.now() - timedelta(days=randint(1, 40), hours=randint(0, 15), minutes=randint(0, 30))

        is_completed = random.random() < 0.7  # 70% chance
        completed_time = None
        if is_completed:
            # Ensure completed is after created time
            completed_time = random_date + timedelta(
                hours=randint(0,15),  # Completed within 1 to 24 hours after creation
                minutes=randint(0, 30)
            )

        current_order = Order(customer=random_customer, created=random_date, completed = completed_time)
        

        db.session.add(current_order)

        num_product_orders = random.randint(4, 6)

        random_prods = db.session.execute(db.select(Product).order_by(db.func.random()).limit(num_product_orders)).scalars()
        for prod in random_prods:
            quantity = random.randint(4, 6)
            db.session.add(ProductOrder(product=prod, quantity=quantity, order=current_order))
        
        
    db.session.commit()

    
# if __name__ == "__main__":
#     if sys.argv[1] == "create":
#         create()
#     elif sys.argv[1] == "drop":
#         drop()
#     elif sys.argv[1] == "import":
#         csvReader("products.csv", Product)
#         csvReader("customers.csv", Customer)

if __name__ == "__main__": 
    with app.app_context(): 
        drop_tables() 
        create_tables()
        csvReader("products.csv", Product)
        csvReader("customers.csv", Customer)
        make_orders()
        make_completed_orders()
        # obj = Category(name="dairy") 
        # db.session.add(obj) 
        # db.session.commit() 
# # USING PUSH 
        # app.app_context().push() 
        # drop_tables() 
        # create_tables()
        # csvReader("products.csv", Product)
        # csvReader("customers.csv", Customer)
        # make_orders()
        # make_completed_orders()
        # obj = Category(name="dairy") 
        # db.session.add(obj) 
        # db.session.commit() 