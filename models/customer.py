from db import db
from flask_security import UserMixin, RoleMixin
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

from .order import Order
from models.customerCoupon import customer_coupons

# --- Association Table for Roles ---
roles_users = db.Table(
    "roles_users",
    db.Column("user_id", db.Integer, db.ForeignKey("Customers.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"))
)

# --- Role Model ---
class Role(db.Model, RoleMixin):
    __tablename__ = "roles"
    id = db.mapped_column(db.Integer, primary_key=True)
    name = db.mapped_column(db.String, unique=True)
    description = db.mapped_column(db.String)
    
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
    github_id = db.mapped_column(db.Integer, nullable=True, unique=True)
    name = db.mapped_column(db.String)
    phone = db.mapped_column(db.String, unique=True)
    email = db.mapped_column(db.String, unique=True, nullable=True)
    active_cart_id = db.mapped_column(db.Integer, nullable=True)

    
    password = db.mapped_column(db.String, nullable=True)
    
    is_admin = db.mapped_column(db.Boolean, default=False)
    
    # Required by Flask-Security-Too
    fs_uniquifier = db.mapped_column(db.String, unique=True, default=lambda: str(uuid.uuid4()))
    active = db.mapped_column(db.Boolean, default=True)
    
    # --- Flask-Security-Too Trackable Fields ---
    last_login_at = db.mapped_column(db.DateTime, nullable=True)
    current_login_at = db.mapped_column(db.DateTime, nullable=True)
    last_login_ip = db.mapped_column(db.String(100), nullable=True)
    current_login_ip = db.mapped_column(db.String(100), nullable=True)
    login_count = db.mapped_column(db.Integer, default=0)

    
    orders = db.relationship("Order", back_populates="customer")
    coupons = db.relationship(
        "Coupon",
        secondary=customer_coupons,
        back_populates="owners"
    )
    roles = db.relationship("Role", secondary=roles_users, backref="customers")



    def __repr__(self):
        return f"{self.name} - {self.phone}"
    
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
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
            },
            "admin": self.is_admin
        }


        return output



