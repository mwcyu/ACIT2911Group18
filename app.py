from flask import Flask, render_template, redirect, url_for, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import Customer,Category,Product,Order,ProductOrder
from pathlib import Path
from db import db
from routes import api_bp, products_bp, customers_bp, categories_bp, orders_bp, practice_bp, cart_bp

app = Flask (__name__)
app.config["SECRET_KEY"] = '13922688c391dba2f50e73a51598e97f1bfb99d739339cc63e87138b171dab1c'

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
app.register_blueprint(cart_bp, url_prefix="/cart" )


# Adjust to your needs / liking. Most likely, you want to use "." for your instance path. This is up to you. You may also use "data"

# flask_login setup
login_manager = LoginManager()
login_manager.login_view = "login_page"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    stmt = db.select(Customer).where(Customer.id == user_id)
    customer = db.session.execute(stmt).scalar()
    return customer


@app.route("/")
def home_page():
    stmt = db.select(Category)
    categories = db.session.execute(stmt).scalars()
    return render_template("base.html", categories=categories, current_user=current_user)


@app.route("/login", methods=["GET", "POST"])
def login_page():
    error_message = None
    if request.method == "POST":
        phone = request.form.get("phone", '').strip()
        password = request.form.get("password", '').strip()

        stmt = db.select(Customer).where(Customer.phone == phone)
        customer = db.session.execute(stmt).scalar_one_or_none()
        
        # Hello
        if customer and customer.password == password:
            login_user(customer)

            print("---- SESSION DATA ----")
            print(dict(session))
            print("----------------------")

            return redirect(url_for('dashboard_page'))
        else:
            error_message = "Invalid phone number or password. Please try again."

    return render_template("login.html", error_message=error_message)


@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        name = request.form.get('name').strip()
        phone = request.form.get('phone').strip()
        password = request.form.get('password').strip()

        stmt = db.select(Customer).where(Customer.phone == phone)
        customer = db.session.execute(stmt).scalar()

        if customer:
            return render_template("register.html", error_message="This phone number already has an account")

        new_customer = Customer(name=name, phone=phone, password=password)
        db.session.add(new_customer)
        db.session.commit()

        return redirect(url_for('login_page'))

    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    
    print(dict(session))
    
    return redirect(url_for("home_page"))


@app.route("/dashboard")
@login_required
def dashboard_page():
    print(current_user.name)
    orders = current_user.orders
    return render_template("dashboard.html", orders=orders)


if __name__ == "__main__":
    app.run(debug=True, port=8888)