from db import db

class ProductOrder(db.Model):
    __tablename__ = "ProductOrder"

    product_id = db.mapped_column(db.ForeignKey("Products.id"), primary_key=True)
    order_id = db.mapped_column(db.ForeignKey("Orders.id"), primary_key=True)
    quantity = db.mapped_column(db.Integer, nullable=False)

    product = db.relationship('Product', back_populates="order")
    order = db.relationship('Order', back_populates='items')

    def __repr__(self):
        return f"Product: {self.product}, Quantity: {self.quantity}, Order ID: {self.order_id}"