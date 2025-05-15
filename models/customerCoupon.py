from db import db
from sqlalchemy import Table, Column, Integer, ForeignKey

# Define the association table for many-to-many relationship
customer_coupons = Table(
    "customer_coupons", db.metadata,
    Column("customer_id", Integer, ForeignKey("Customers.id"), primary_key=True),
    Column("coupon_id", Integer, ForeignKey("coupons.id"), primary_key=True)
)

