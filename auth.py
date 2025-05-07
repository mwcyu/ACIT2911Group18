from flask_login import LoginManager
from db import db
from models import Customer

login_manager = LoginManager()

def init_login_manager(app):
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    stmt = db.select(Customer).where(Customer.id == user_id)
    return db.session.execute(stmt).scalar_one_or_none()