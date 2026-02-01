from flask import Blueprint, request, jsonify
from flask_socketio import emit
import redis
import json

notifications_bp = Blueprint("notifications", __name__)

# Redis client for pub/sub
redis_client = None

def init_redis(app):
    """Initialize Redis client"""
    global redis_client
    redis_url = app.config.get("REDIS_URL", "redis://redis:6379/0")
    redis_client = redis.from_url(redis_url)

@notifications_bp.post("/send")
def send_notification():
    """Send a notification via WebSocket"""
    data = request.get_json(silent=True) or {}
    
    event_type = data.get("event_type", "notification")
    message = data.get("message", "")
    user_id = data.get("user_id")
    
    if not message:
        return jsonify({"detail": "Message is required"}), 400
    
    # Publish to Redis for WebSocket distribution
    if redis_client:
        try:
            payload = {
                "event_type": event_type,
                "message": message,
                "user_id": user_id,
            }
            redis_client.publish("notifications", json.dumps(payload))
        except Exception as e:
            return jsonify({"detail": f"Failed to publish notification: {str(e)}"}), 500
    
    return jsonify({"detail": "Notification sent"}), 200

@notifications_bp.post("/broadcast")
def broadcast_message():
    """Broadcast a message to all connected clients"""
    data = request.get_json(silent=True) or {}
    
    message = data.get("message", "")
    event_type = data.get("event_type", "broadcast")
    
    if not message:
        return jsonify({"detail": "Message is required"}), 400
    
    # Publish to Redis for WebSocket distribution
    if redis_client:
        try:
            payload = {
                "event_type": event_type,
                "message": message,
            }
            redis_client.publish("notifications", json.dumps(payload))
        except Exception as e:
            return jsonify({"detail": f"Failed to broadcast: {str(e)}"}), 500
    
    return jsonify({"detail": "Message broadcasted"}), 200

@notifications_bp.get("/health")
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "notification-service"}), 200
