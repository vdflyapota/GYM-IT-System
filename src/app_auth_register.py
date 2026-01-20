# Example of registering auth_bp if it's not already in your app.py
from .auth.api import auth_bp
# inside create_app():
app.register_blueprint(auth_bp, url_prefix="/auth")
