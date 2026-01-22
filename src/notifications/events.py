from flask import current_app

def emit_leaderboard_update(leaderboard):
    socketio = current_app.extensions.get("socketio")
    if not socketio:
        current_app.logger.warning("SocketIO not initialized; skipping leaderboard emit.")
        return
    socketio.emit("leaderboard_update", {"leaderboard": leaderboard}, broadcast=True)
