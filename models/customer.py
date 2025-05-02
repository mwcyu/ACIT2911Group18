from db import db
from flask_login import UserMixin

from .order import Order

class Customer(db.Model, UserMixin):
    """
    UserMixin gives Customer:
    is_authenticated
    is_active
    is_anonymous
    is_id()
    """
    __tablename__ = "Customers"

    id = db.mapped_column(db.Integer, primary_key=True)
    name = db.mapped_column(db.String)
    phone = db.mapped_column(db.String, unique=True)
    
    password = db.mapped_column(db.String, nullable=False)
    
    orders = db.relationship("Order", back_populates="customer")

    def __repr__(self):
        return f"{self.name} - {self.phone}"
    
    
    def to_json(self):
        pending_orders = [order for order in self.orders if order.completed == None]
        
        completed_orders = [order for order in self.orders if order.completed]
        
        output = {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "orders": {
                "completed_order" : [order.to_json() for order in completed_orders],
                "pending_orders" : [order.to_json() for order in pending_orders]
            }
        }


        return output
    






