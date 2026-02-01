from flask import Flask, request, jsonify
import socket

app = Flask(__name__)

# In-memory notification storage (for demo)
notifications = []

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "notification-service",
        "hostname": socket.gethostname(),
        "notifications_count": len(notifications)
    })

@app.route('/api/notifications', methods=['POST'])
def create_notification():
    data = request.json
    notification = {
        "id": len(notifications) + 1,
        "type": data.get('type', 'info'),
        "title": data.get('title', 'Notification'),
        "message": data.get('message', ''),
        "user_id": data.get('user_id'),
        "timestamp": datetime.now().isoformat(),
        "read": False
    }
    notifications.append(notification)
    
    # Log the notification (in real app, would send email/websocket)
    print(f"📧 Notification created: {notification['title']}")
    
    return jsonify(notification), 201

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    user_id = request.args.get('user_id')
    if user_id:
        user_notifications = [n for n in notifications if n.get('user_id') == user_id]
        return jsonify(user_notifications)
    return jsonify(notifications[:50])  # Return latest 50

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8004, debug=True)