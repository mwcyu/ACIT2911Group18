from db import db
from decimal import Decimal


class Order(db.Model):
    __tablename__ = "Orders"

    id = db.mapped_column(db.Integer, primary_key=True)
    customer_id = db.mapped_column(db.Integer, db.ForeignKey("Customers.id"))

    # db.func.now() is NOW()
    created = db.mapped_column(db.DateTime, nullable=False, default=db.func.now())
    completed = db.mapped_column(db.DateTime, nullable=True, default=None)
    amount = db.mapped_column(db.Float(6,2), nullable=True, default=None)
    name = db.mapped_column(db.String(100), nullable=True, default="Untitled Cart")

    items = db.relationship('ProductOrder', back_populates="order")
    customer = db.relationship('Customer', back_populates='orders')

    def __repr__(self):
        return f"ID:{self.id} Items:{[item for item in self.items]} Customer: {self.customer}"

    def estimate(self):
        total = 0
        for item in self.items:
            total += item.quantity * item.product.price
        
        return float(round(total,2))
    
    def complete(self):
        products_to_update = []
        for item in self.items:
            if item.quantity > item.product.available:
                raise ValueError
            products_to_update.append({"product": item.product, "removing": item.quantity})
        
        for product in products_to_update:
            product["product"].available -= product["removing"]
        self.completed = db.func.now()
        self.amount = self.estimate()
        
        if self.customer.active_cart_id == self.id:
            self.customer.active_cart_id = None

    def to_json(self):
        completed = False
        price_string = "estimated_total"
        price_value = self.estimate()
        if self.completed:
            completed = True
            price_string = "amount"
            price_value = self.amount
        

# {field.name: getattr(self, field.name) for field in self.__table__.columns}
        output = {
            "id": self.id,
            "customer_name": self.customer.name,
            "completed": completed,
            "created": self.created,
            price_string: price_value,
            "products": [
                {
                    "inventory": item.product.available,
                    "name": item.product.name,
                    "price": item.product.price,
                    "quantity": item.quantity,
                    "category": item.product.category.name}
                    for item in self.items
            ]
        }

        if self.completed:
            output["completed_date"] = self.completed
        
        return output
        