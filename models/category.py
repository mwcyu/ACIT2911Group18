from db import db

class Category(db.Model):
    __tablename__ = "Categories"

    id = db.mapped_column(db.Integer, primary_key=True)
    name = db.mapped_column(db.String)
    
    products = db.relationship("Product",back_populates="category")

    def __repr__(self):
        return f"{self.id}: {self.name}"
    

    def to_json(self):
        output = {
            "id": self.id,
            "name": self.name,
            # "products": [product.to_json() for product in self.products]
        }
        return output