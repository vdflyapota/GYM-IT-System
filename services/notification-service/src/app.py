from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
import redis
import json
from .config import Config
from .api import notifications_bp, init_redis

socketio = SocketIO(cors_allowed_origins="*", async_mode="eventlet")

def create_app():
    """Create and configure the notification service Flask app"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # CORS
    CORS(app, origins=app.config.get("CORS_ORIGINS"))

    # Initialize Redis
    init_redis(app)

    # Register blueprints
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")

    @app.route("/healthz")
    def healthz():
        return {"status": "ok", "service": "notification-service"}, 200

    return app

def listen_to_redis(app):
    """Listen to Redis pub/sub and emit to WebSocket clients"""
    redis_url = app.config.get("REDIS_URL", "redis://redis:6379/0")
    r = redis.from_url(redis_url)
    pubsub = r.pubsub()
    pubsub.subscribe("notifications")
    
    for message in pubsub.listen():
        if message["type"] == "message":
            try:
                data = json.loads(message["data"])
                event_type = data.get("event_type", "notification")
                socketio.emit(event_type, data)
            except Exception as e:
                app.logger.error(f"Error processing Redis message: {e}")

if __name__ == "__main__":
    app = create_app()
    socketio.init_app(app)
    
    # Start Redis listener in background
    import threading
    redis_thread = threading.Thread(target=listen_to_redis, args=(app,), daemon=True)
    redis_thread.start()
    
    socketio.run(app, host="0.0.0.0", port=8004, debug=True)
