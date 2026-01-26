from flask import Flask, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from .config import Config
from .gateway import get_target_service, proxy_request

def create_app():
    """Create and configure the API Gateway Flask app"""
    # Serve static files from the main project
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    static_dir = os.path.join(root_dir, "static")
    
    app = Flask(__name__, static_folder=static_dir, static_url_path="/")
    app.config.from_object(Config)

    # CORS
    CORS(app, origins=app.config.get("CORS_ORIGINS"))

    # JWT for token validation
    JWTManager(app)

    @app.route("/healthz")
    def healthz():
        return {"status": "ok", "service": "api-gateway"}, 200

    @app.route("/api/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    def api_proxy(path):
        """Route API requests to appropriate microservice"""
        full_path = f"/api/{path}"
        service_url, _ = get_target_service(full_path)
        return proxy_request(service_url, full_path)

    @app.route("/")
    def index():
        """Serve the main index.html"""
        return send_from_directory(app.static_folder, "index.html")

    @app.route("/<path:path>")
    def static_files(path):
        """Serve static files"""
        return send_from_directory(app.static_folder, path)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)
