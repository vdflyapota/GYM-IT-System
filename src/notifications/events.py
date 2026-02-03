from flask import current_app


def emit_leaderboard_update(leaderboard):
    socketio = current_app.extensions.get("socketio")
    if not socketio:
        current_app.logger.warning("SocketIO not initialized; skipping leaderboard emit.")
        return
    socketio.emit("leaderboard_update", {"leaderboard": leaderboard}, broadcast=True)


def emit_new_notification(user_id: int, title: str, message: str = "", notif_type: str = "info"):
    """Emit a new_notification event; client should show toast only when user_id matches."""
    socketio = current_app.extensions.get("socketio")
    if not socketio:
        return
    socketio.emit(
        "new_notification",
        {"user_id": user_id, "title": title, "message": message, "type": notif_type},
        broadcast=True,
    )
