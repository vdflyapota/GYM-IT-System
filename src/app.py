import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from prometheus_flask_exporter import PrometheusMetrics

from .config import Config
from .auth.jwt import init_jwt
from .auth.rbac import add_rbac_error_handlers
from .observability.logging import configure_logging
from .observability.metrics import register_custom_metrics
from .common.db import init_db

# Blueprints
from .auth.api import auth_bp
from .users.api import users_bp
from .tournaments.api import tournaments_bp
from .notifications.api import notifications_bp

# Optional blueprints
try:
    from .challenges.api import challenges_bp
    HAS_CHALLENGES = True
except Exception:
    HAS_CHALLENGES = False

socketio = SocketIO(cors_allowed_origins="*", async_mode="eventlet")


def create_app():
    # Absolute path to top-level static/ directory
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    static_dir = os.path.join(root_dir, "static")

    # Serve static/ at root ("/")
    app = Flask(__name__, static_folder=static_dir, static_url_path="/")
    app.config.from_object(Config)

    # CORS + logging
    CORS(app)
    configure_logging(app)

    # DB + JWT + RBAC handlers
    init_db(app)          # creates tables on first run
    init_jwt(app)
    add_rbac_error_handlers(app)

    # Observability
    PrometheusMetrics(app)  # /metrics
    register_custom_metrics(app)

    # Register blueprints matching frontend fetch() paths
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(tournaments_bp, url_prefix="/tournaments")
    if HAS_CHALLENGES:
        app.register_blueprint(challenges_bp, url_prefix="/challenges")
    app.register_blueprint(notifications_bp, url_prefix="/notifications")

    @app.route("/healthz")
    def healthz():
        return {"status": "ok"}, 200

    # Home page → static/index.html
    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    return app


if __name__ == "__main__":
    app = create_app()
    socketio.init_app(app)
    socketio.run(app, host="0.0.0.0", port=8080)
