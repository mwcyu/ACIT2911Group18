from flask_dance.contrib.github import make_github_blueprint
import os

def init_oauth(app):
    github_bp = make_github_blueprint(
        client_id=os.getenv('GITHUB_CLIENT_ID'),
        client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
        scope=['user:email']  # Request access to user's email
    )
    app.register_blueprint(github_bp, url_prefix="/login")
    return github_bp