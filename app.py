from flask import Flask, render_template, redirect, url_for
from models import Customer,Category,Product,Order,ProductOrder
from pathlib import Path
from db import db
from routes import api_bp, products_bp, customers_bp, categories_bp, orders_bp, practice_bp

app = Flask (__name__)


# @app.route("/")
# def home():
#     return render_template("home.html", my_list=[]"Tim", "Bob", "Alice")

# This will make Flask use a 'sqlite' database with the filename provided 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project1.db"
 # This will make Flask store the database file in the path provided 
app.instance_path = Path(".").resolve()

db.init_app(app)

# registering a blueprint
app.register_blueprint(api_bp, url_prefix="/api")

# Blueprint for HTML
app.register_blueprint(products_bp, url_prefix="/products")
app.register_blueprint(orders_bp, url_prefix="/orders")
app.register_blueprint(categories_bp, url_prefix="/categories")
app.register_blueprint(customers_bp, url_prefix="/customers")
app.register_blueprint(practice_bp,url_prefix="/practice")


# Adjust to your needs / liking. Most likely, you want to use "." for your instance path. This is up to you. You may also use "data"

@app.route("/")
def home_page():
    cat_stmt = db.select(Category)
    categories = db.session.execute(cat_stmt).scalars()
    return render_template("base.html", categories=categories)


if __name__ == "__main__":
    app.run(debug=True, port=8888)