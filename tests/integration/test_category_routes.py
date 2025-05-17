import pytest
from models import Category, Product
from ..conftest import assert_flashed_message

class TestCategoryRoutes:

    def test_categories_page_loads(self, client, db):
        category1 = Category(name="Fruits")
        category2 = Category(name="Dairy")
        db.session.add_all([category1, category2])
        db.session.commit()

        response = client.get("/categories/")
        assert response.status_code == 200
        assert b"Fruits" in response.data
        assert b"Dairy" in response.data

    def test_category_detail_page_valid(self, client, db, test_category):
        product1 = Product(name="Apple", price=1.00, available=5, in_season=True, category=test_category)
        product2 = Product(name="Banana", price=1.50, available=10, in_season=False, category=test_category)
        db.session.add_all([product1, product2])
        db.session.commit()

        response = client.get(f"/categories/{test_category.name}")
        assert response.status_code == 200
        assert b"Apple" in response.data
        assert b"Banana" in response.data
        assert test_category.name.encode() in response.data

    def test_category_detail_page_404(self, client):
        response = client.get("/categories/NonExistentCategory")
        assert response.status_code == 404
