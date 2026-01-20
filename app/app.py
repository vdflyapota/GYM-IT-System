from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from prometheus_flask_exporter import PrometheusMetrics

from .auth.jwt import init_jwt
from .auth.rbac import add_rbac_error_handlers
from .observability.logging import configure_logging
from .observability.metrics import register_custom_metrics
from .common.db import init_db
from .tournaments.api import tournaments_bp
from .users.api import users_bp
from .reporting.api import reporting_bp
from .notifications.api import notifications_bp

socketio = SocketIO(cors_allowed_origins="*", async_mode="eventlet")

def create_app():
    app = Flask(__name__)
    app.config.from_object("src.config.Config")

    CORS(app)
    configure_logging(app)

    # DB and JWT setup
    init_db(app)
    init_jwt(app)
    add_rbac_error_handlers(app)

    # Observability
    PrometheusMetrics(app)
    register_custom_metrics(app)

    # Blueprints
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(tournaments_bp, url_prefix="/api/tournaments")
    app.register_blueprint(reporting_bp, url_prefix="/api/reporting")
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")

    # Health endpoints
    @app.route("/healthz")
    def healthz():
        return {"status": "ok"}, 200

    return app

if __name__ == "__main__":
    app = create_app()
    socketio.init_app(app)
    socketio.run(app, host="0.0.0.0", port=8080)
