from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config import Config
from .models import init_db
from .api import tournaments_bp

def create_app():
    """Create and configure the tournament service Flask app"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # CORS
    CORS(app, origins=app.config.get("CORS_ORIGINS"))

    # JWT
    JWTManager(app)

    # Database
    init_db(app)

    # Register blueprints
    app.register_blueprint(tournaments_bp, url_prefix="/api/tournaments")

    @app.route("/healthz")
    def healthz():
        return {"status": "ok", "service": "tournament-service"}, 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8003, debug=True)
