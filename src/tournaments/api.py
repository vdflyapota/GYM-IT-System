from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..auth.rbac import require_role
from .engine import compute_leaderboard
from ..notifications.events import emit_leaderboard_update

tournaments_bp = Blueprint("tournaments", __name__)

@tournaments_bp.post("/")
@jwt_required()
@require_role("trainer", "admin")
def submit_result():
    payload = request.get_json() or {}
    # TODO: persist result in DB
    # For now, compute from a placeholder list
    sample_results = [
        {"member_id": 1, "member_name": "Alice", "points": 3},
        {"member_id": 2, "member_name": "Bob", "points": 1},
        {"member_id": 1, "member_name": "Alice", "points": 2},
    ]
    leaderboard = compute_leaderboard(sample_results)
    emit_leaderboard_update(leaderboard)
    return {"message": "result recorded"}, 200

@tournaments_bp.get("/leaderboard")
def leaderboard():
    # TODO: fetch results from DB and compute
    sample_results = [
        {"member_id": 1, "member_name": "Alice", "points": 5},
        {"member_id": 2, "member_name": "Bob", "points": 1},
    ]
    return {"leaderboard": compute_leaderboard(sample_results)}, 200
