from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config
from .models import init_db
from .api import auth_bp

def create_app():
    """Create and configure the auth service Flask app"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # CORS
    CORS(app, origins=app.config.get("CORS_ORIGINS"))

    # JWT
    JWTManager(app)

    # Database
    init_db(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    @app.route("/healthz")
    def healthz():
        return {"status": "ok", "service": "auth-service"}, 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8001, debug=True)
