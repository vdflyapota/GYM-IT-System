from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from ..auth.rbac import require_role
from .engine import compute_leaderboard, generate_single_elimination_bracket, generate_double_elimination_bracket
from ..notifications.events import emit_leaderboard_update
from src.common.db import db
from .models import Tournament, Participant, Bracket
from src.users.models import User
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
        start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return {"error": "Invalid start date format"}, 400

    # Create tournament
    tournament = Tournament(
        name=name,
        start_date=start_dt,
        max_participants=max_participants,
        tournament_type=tournament_type,
        status="setup",
    )

    db.session.add(tournament)
    db.session.commit()

    return {"tournament": tournament.to_dict(), "message": "Tournament created successfully"}, 201


@tournaments_bp.get("/")
def list_tournaments():
    """List all tournaments"""
    tournaments = Tournament.query.order_by(Tournament.created_at.desc()).all()
    return [t.to_dict() for t in tournaments], 200


@tournaments_bp.get("/<int:tournament_id>")
def get_tournament(tournament_id):
    """Get a specific tournament"""
    tournament = db.session.get(Tournament, tournament_id)
    if not tournament:
        return {"error": "Tournament not found"}, 404

    return {"tournament": tournament.to_dict()}, 200


@tournaments_bp.put("/<int:tournament_id>/participants")
@jwt_required()
@require_role("trainer", "admin")
def assign_participants(tournament_id):
    """Assign participants to a tournament"""
    tournament = db.session.get(Tournament, tournament_id)
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
        return {
            "error": (
                f"Cannot add {new_count} participants. "
                f"Maximum is {tournament.max_participants}, current count is {current_count}"
            )
        }, 400

    # Add participants
    added_participants = []
    for idx, p_data in enumerate(participants_data):
        name = p_data.get("name")
        user_id = p_data.get("user_id")

        if not name:
            continue

        participant = Participant(tournament_id=tournament_id, user_id=user_id, name=name, seed=current_count + idx + 1)
        db.session.add(participant)
        added_participants.append(participant)

    db.session.commit()

    return {
        "message": f"Added {len(added_participants)} participants",
        "participants": [p.to_dict() for p in added_participants],
    }, 200


@tournaments_bp.get("/<int:tournament_id>/participants")
def get_participants(tournament_id):
    """Get participants for a tournament"""
    tournament = db.session.get(Tournament, tournament_id)
    if not tournament:
        return {"error": "Tournament not found"}, 404

    return {"participants": [p.to_dict() for p in tournament.participants]}, 200


@tournaments_bp.get("/<int:tournament_id>/bracket")
def get_bracket(tournament_id):
    """Generate and return the bracket for a tournament"""
    tournament = db.session.get(Tournament, tournament_id)
    if not tournament:
        return {"error": "Tournament not found"}, 404

    # Check if bracket already exists
    existing_brackets = Bracket.query.filter_by(tournament_id=tournament_id).all()

    if existing_brackets:
        # Return existing bracket
        return {"tournament": tournament.to_dict(), "bracket": [b.to_dict() for b in existing_brackets]}, 200

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
            score=b_data.get("score"),
        )
        db.session.add(bracket)
        brackets.append(bracket)

    # Update tournament status to active
    tournament.status = "active"
    db.session.commit()

    return {"tournament": tournament.to_dict(), "bracket": [b.to_dict() for b in brackets]}, 200


@tournaments_bp.get("/available-users")
@jwt_required()
@require_role("trainer", "admin")
def get_available_users():
    """Get list of active users that can be added to tournaments"""
    users = User.query.filter_by(is_active=True, is_approved=True, is_banned=False).all()
    return {
        "users": [
            {"id": u.id, "name": u.full_name, "email": u.email, "role": u.role} for u in users
        ]
    }, 200


@tournaments_bp.put("/<int:tournament_id>/bracket/<int:bracket_id>/result")
@jwt_required()
@require_role("trainer", "admin")
def record_match_result(tournament_id, bracket_id):
    """Record the result of a bracket match"""
    tournament = db.session.get(Tournament, tournament_id)
    if not tournament:
        return {"error": "Tournament not found"}, 404

    bracket = db.session.get(Bracket, bracket_id)
    if not bracket or bracket.tournament_id != tournament_id:
        return {"error": "Bracket match not found"}, 404

    payload = request.get_json(silent=True) or {}
    winner_id = payload.get("winner_id")
    score = payload.get("score")

    if not winner_id:
        return {"error": "Winner ID is required"}, 400

    # Verify winner is one of the participants in this match
    if winner_id not in [bracket.participant1_id, bracket.participant2_id]:
        return {"error": "Winner must be one of the match participants"}, 400

    # Update bracket with result
    bracket.winner_id = winner_id
    if score:
        bracket.score = score

    # Check if we need to advance winner to next round
    current_round = bracket.round
    current_match = bracket.match_number

    # Find next round match (winner advances)
    next_round = current_round + 1
    next_match = (current_match + 1) // 2  # Two matches feed into one in next round

    next_bracket = Bracket.query.filter_by(
        tournament_id=tournament_id, round=next_round, match_number=next_match
    ).first()

    if next_bracket:
        # Determine if winner goes to participant1 or participant2 slot
        if current_match % 2 == 1:  # Odd match number goes to participant1
            next_bracket.participant1_id = winner_id
        else:  # Even match number goes to participant2
            next_bracket.participant2_id = winner_id

    db.session.commit()

    return {
        "message": "Match result recorded successfully",
        "bracket": bracket.to_dict(),
    }, 200


# Legacy endpoints for backward compatibility
@tournaments_bp.post("/result")
@jwt_required()
@require_role("trainer", "admin")
def submit_result():
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
    """Get leaderboard with user ranks and points"""
    # Fetch all participants with user information
    participants = Participant.query.filter(Participant.user_id.isnot(None)).all()
    
    # Compute points: 1 point per tournament participation, 3 points per win
    user_points = {}
    user_info = {}
    
    for participant in participants:
        if not participant.user:
            continue
            
        user_id = participant.user_id
        if user_id not in user_points:
            user_points[user_id] = 0
            user_info[user_id] = {
                'email': participant.user.email,
                'full_name': participant.user.full_name
            }
        
        # 1 point per tournament participation
        user_points[user_id] += 1
    
    # Add points for wins
    brackets = Bracket.query.filter(Bracket.winner_id.isnot(None)).all()
    for bracket in brackets:
        if bracket.winner and bracket.winner.user_id:
            winner_id = bracket.winner.user_id
            if winner_id in user_points:
                user_points[winner_id] += 3  # 3 points per win
    
    # Build leaderboard
    leaderboard_data = []
    for user_id, points in user_points.items():
        info = user_info.get(user_id, {})
        leaderboard_data.append({
            'user_id': user_id,
            'user_name': info.get('full_name', 'Unknown'),
            'email': info.get('email', ''),
            'points': points
        })
    
    # Sort by points (descending)
    leaderboard_data.sort(key=lambda x: (-x['points'], x['user_name']))
    
    # Add rank
    for idx, entry in enumerate(leaderboard_data):
        entry['rank'] = idx + 1
    
    return {"leaderboard": leaderboard_data}, 200
