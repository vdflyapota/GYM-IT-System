from flask import Flask, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os
from .config import Config
from .gateway import get_target_service, proxy_request

def create_app():
    """Create and configure the API Gateway Flask app"""
    # Static files are mounted at /app/static in the container (via docker-compose volumes)
    static_dir = '/app/static'
    
    # Fallback for local development outside Docker
    if not os.path.exists(static_dir):
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        static_dir = os.path.join(root_dir, "static")
    
    app = Flask(__name__, static_folder=static_dir, static_url_path="")
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
        try:
            return send_from_directory(app.static_folder, "index.html")
        except Exception as e:
            app.logger.error(f"Error serving index.html: {e}")
            app.logger.error(f"Static folder: {app.static_folder}")
            return {"error": "Static files not found", "static_folder": app.static_folder}, 404

    @app.route("/<path:path>")
    def static_files(path):
        """Serve static files (CSS, JS, images, HTML pages, etc.)"""
        # Don't serve API routes as static files
        if path.startswith('api/'):
            return {"error": "Not found"}, 404
        
        try:
            # Try to serve the exact file requested
            file_path = os.path.join(app.static_folder, path)
            if os.path.isfile(file_path):
                return send_from_directory(app.static_folder, path)
            
            # If no file extension and not found, try adding .html
            if '.' not in path:
                html_path = f"{path}.html"
                html_file = os.path.join(app.static_folder, html_path)
                if os.path.isfile(html_file):
                    return send_from_directory(app.static_folder, html_path)
            
            # Not found
            app.logger.warning(f"Static file not found: {path}")
            return {"error": "File not found", "path": path}, 404
        except Exception as e:
            app.logger.error(f"Error serving static file {path}: {e}")
            return {"error": "Internal server error"}, 500

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)
