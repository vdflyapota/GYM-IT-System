from flask import Blueprint

challenges_bp = Blueprint("challenges", __name__)

@challenges_bp.get("/leaderboard")
def get_leaderboard():
    # TODO: replace with real aggregation
    data = [
        {"user_name": "Alice", "total_score": 42},
        {"user_name": "Bob", "total_score": 31},
        {"user_name": "Charlie", "total_score": 27},
    ]
    return data, 200
