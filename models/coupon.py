from db import db
from models.customerCoupon import customer_coupons

class Coupon(db.Model):
    __tablename__ = "coupons"

    id = db.mapped_column(db.Integer, primary_key=True)
    code = db.mapped_column(db.String, unique=True, nullable=False)
    description = db.mapped_column(db.String, nullable=True)
    minimum_purchase = db.mapped_column(db.Float, nullable=True)  # Minimum order value to apply coupon
    discount_amount = db.mapped_column(db.Float, nullable=False)  # Discount value (could be percent or fixed)
    is_percent = db.mapped_column(db.Boolean, default=False)      # True if discount_amount is a percent
    active = db.mapped_column(db.Boolean, default=True)
    # Relationship to customers who own this coupon
    owners = db.relationship(
        "Customer",
        secondary=customer_coupons,
        back_populates="coupons"
    )

    def __repr__(self):
        return f"<Coupon {self.code} - {'%' if self.is_percent else '$'}{self.discount_amount}"

    def to_json(self):
        return {
            "id": self.id,
            "code": self.code,
            "description": self.description,
            "minimum_purchase": self.minimum_purchase,
            "discount_amount": self.discount_amount,
            "is_percent": self.is_percent,
            "active": self.active
        }