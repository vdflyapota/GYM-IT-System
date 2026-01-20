from flask_socketio import emit

def emit_leaderboard_update(leaderboard):
    emit("leaderboard_update", {"leaderboard": leaderboard}, broadcast=True)
