# routes/__init__.py

from .api import api_bp
from .auth import auth_bp
from .admin import admin_bp
from .cart import cart_bp
from .categories import categories_bp
from .customers import customers_bp
from .orders import orders_bp
from .products import products_bp

__all__ = [
    "register_blueprints",
    "api_bp",
    "auth_bp",
    "admin_bp",
    "cart_bp",
    "categories_bp",
    "customers_bp",
    "orders_bp",
    "products_bp",
]

def register_blueprints(app):
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(cart_bp, url_prefix="/cart")
    app.register_blueprint(categories_bp, url_prefix="/categories")
    app.register_blueprint(customers_bp, url_prefix="/customers")
    app.register_blueprint(orders_bp, url_prefix="/orders")
    app.register_blueprint(products_bp, url_prefix="/products")