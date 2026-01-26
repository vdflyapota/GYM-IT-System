from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..auth.rbac import require_role
from .engine import compute_leaderboard, generate_single_elimination_bracket, generate_double_elimination_bracket
from ..notifications.events import emit_leaderboard_update
from src.common.db import db
from .models import Tournament, Participant, Bracket
from datetime import datetime

tournaments_bp = Blueprint("tournaments", __name__)


@tournaments_bp.post("/")
@jwt_required()
@require_role("trainer", "admin")
def create_tournament():
    """Create a new tournament"""
    payload = request.get_json(silent=True) or {}
    
    name = payload.get("name")
    start_date = payload.get("start_date")
    max_participants = payload.get("max_participants", 8)
    tournament_type = payload.get("tournament_type", "single_elimination")
    
    if not name:
        return {"error": "Tournament name is required"}, 400
    
    if not start_date:
        return {"error": "Start date is required"}, 400
    
    try:
        # Parse start date
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        return {"error": "Invalid start date format"}, 400
    
    # Create tournament
    tournament = Tournament(
        name=name,
        start_date=start_dt,
        max_participants=max_participants,
        tournament_type=tournament_type,
        status="setup"
    )
    
    db.session.add(tournament)
    db.session.commit()
    
    return {"tournament": tournament.to_dict(), "message": "Tournament created successfully"}, 201


@tournaments_bp.get("/")
def list_tournaments():
    """List all tournaments"""
    tournaments = Tournament.query.order_by(Tournament.created_at.desc()).all()
    return {"tournaments": [t.to_dict() for t in tournaments]}, 200


@tournaments_bp.get("/<int:tournament_id>")
def get_tournament(tournament_id):
    """Get a specific tournament"""
    tournament = Tournament.query.get(tournament_id)
    if not tournament:
        return {"error": "Tournament not found"}, 404
    
    return {"tournament": tournament.to_dict()}, 200


@tournaments_bp.put("/<int:tournament_id>/participants")
@jwt_required()
@require_role("trainer", "admin")
def assign_participants(tournament_id):
    """Assign participants to a tournament"""
    tournament = Tournament.query.get(tournament_id)
    if not tournament:
        return {"error": "Tournament not found"}, 404
    
    payload = request.get_json(silent=True) or {}
    participants_data = payload.get("participants", [])
    
    if not participants_data:
        return {"error": "Participants list is required"}, 400
    
    # Check if adding participants would exceed max
    current_count = len(tournament.participants)
    new_count = len(participants_data)
    
    if current_count + new_count > tournament.max_participants:
        return {"error": f"Cannot add {new_count} participants. Maximum is {tournament.max_participants}, current count is {current_count}"}, 400
    
    # Add participants
    added_participants = []
    for idx, p_data in enumerate(participants_data):
        name = p_data.get("name")
        user_id = p_data.get("user_id")
        
        if not name:
            continue
        
        participant = Participant(
            tournament_id=tournament_id,
            user_id=user_id,
            name=name,
            seed=current_count + idx + 1
        )
        db.session.add(participant)
        added_participants.append(participant)
    
    db.session.commit()
    
    return {
        "message": f"Added {len(added_participants)} participants",
        "participants": [p.to_dict() for p in added_participants]
    }, 200


@tournaments_bp.get("/<int:tournament_id>/participants")
def get_participants(tournament_id):
    """Get participants for a tournament"""
    tournament = Tournament.query.get(tournament_id)
    if not tournament:
        return {"error": "Tournament not found"}, 404
    
    return {"participants": [p.to_dict() for p in tournament.participants]}, 200


@tournaments_bp.get("/<int:tournament_id>/bracket")
def get_bracket(tournament_id):
    """Generate and return the bracket for a tournament"""
    tournament = Tournament.query.get(tournament_id)
    if not tournament:
        return {"error": "Tournament not found"}, 404
    
    # Check if bracket already exists
    existing_brackets = Bracket.query.filter_by(tournament_id=tournament_id).all()
    
    if existing_brackets:
        # Return existing bracket
        return {
            "tournament": tournament.to_dict(),
            "bracket": [b.to_dict() for b in existing_brackets]
        }, 200
    
    # Generate new bracket
    participants = tournament.participants
    
    if not participants:
        return {"error": "No participants assigned to tournament"}, 400
    
    # Generate bracket based on tournament type
    if tournament.tournament_type == "double_elimination":
        bracket_data = generate_double_elimination_bracket(participants)
    else:
        bracket_data = generate_single_elimination_bracket(participants)
    
    # Save bracket to database
    brackets = []
    for b_data in bracket_data:
        bracket = Bracket(
            tournament_id=tournament_id,
            round=b_data["round"],
            match_number=b_data["match_number"],
            participant1_id=b_data["participant1_id"],
            participant2_id=b_data["participant2_id"],
            winner_id=b_data.get("winner_id"),
            score=b_data.get("score")
        )
        db.session.add(bracket)
        brackets.append(bracket)
    
    # Update tournament status to active
    tournament.status = "active"
    db.session.commit()
    
    return {
        "tournament": tournament.to_dict(),
        "bracket": [b.to_dict() for b in brackets]
    }, 200


# Legacy endpoints for backward compatibility
@tournaments_bp.post("/result")
@jwt_required()
@require_role("trainer", "admin")
def submit_result():
    payload = request.get_json(silent=True) or {}
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
