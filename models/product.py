from db import db

class Product(db.Model):
    __tablename__ = "Products"

    id = db.mapped_column(db.Integer, primary_key=True)
    name = db.mapped_column(db.String)
    price = db.mapped_column(db.DECIMAL(10, 2))
    available = db.mapped_column(db.Integer, default=0)
    category_id = db.mapped_column(db.Integer, db.ForeignKey("Categories.id"))
    in_season = db.mapped_column(db.Boolean, default=False)
    season_name = db.mapped_column(db.String, db.ForeignKey("Seasons.name"))
    
    category = db.relationship("Category", back_populates="products")
    order = db.relationship("ProductOrder", back_populates="product")
    season = db.relationship("Season", back_populates="products")

    def __repr__(self):
        # return f"{self.name} Price: ${self.price} Inventory: {self.available} Category: {self.category.name} Field: {self.__table__.columns}"
        return f"Field: {[field.name for field in self.__table__.columns]}"
    
    def to_json(self):
        # output= {field.name: getattr(self, field.name) for field in self.__table__.columns}
        # return output
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "inventory": self.available,
            "category_id": self.category_id,
            "category": self.category.name,
            "seasonal": self.seasonal
        }