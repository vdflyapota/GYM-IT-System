from src.app import create_app, socketio

if __name__ == "__main__":
    app = create_app()
    socketio.init_app(app)
    socketio.run(app, host="0.0.0.0", port=8080)
