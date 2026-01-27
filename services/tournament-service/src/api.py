from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from datetime import datetime
from .models import db, Tournament, Participant, Bracket

tournaments_bp = Blueprint("tournaments", __name__)

def get_current_user_role():
    """Helper to get current user role from JWT"""
    claims = get_jwt()
    return claims.get("role", "member")

def require_trainer_or_admin():
    """Helper to check if current user is trainer or admin"""
    role = get_current_user_role()
    if role not in ["trainer", "admin"]:
        return jsonify({"detail": "Trainer or Admin access required"}), 403
    return None

@tournaments_bp.post("/")
@jwt_required()
def create_tournament():
    """Create a new tournament"""
    error = require_trainer_or_admin()
    if error:
        return error
    
    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    start_date = payload.get("start_date")
    max_participants = payload.get("max_participants", 8)
    tournament_type = payload.get("tournament_type", "single_elimination")

    if not name:
        return jsonify({"detail": "Tournament name is required"}), 400

    if not start_date:
        return jsonify({"detail": "Start date is required"}), 400

    try:
        start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return jsonify({"detail": "Invalid start date format"}), 400

    tournament = Tournament(
        name=name,
        start_date=start_dt,
        max_participants=max_participants,
        tournament_type=tournament_type,
        status="setup",
    )

    db.session.add(tournament)
    db.session.commit()

    return jsonify({"tournament": tournament.to_dict(), "message": "Tournament created successfully"}), 201

@tournaments_bp.get("/")
@jwt_required()
def list_tournaments():
    """List all tournaments"""
    tournaments = Tournament.query.all()
    return jsonify({"tournaments": [t.to_dict() for t in tournaments]}), 200

@tournaments_bp.get("/<int:tournament_id>")
@jwt_required()
def get_tournament(tournament_id):
    """Get tournament by ID"""
    tournament = Tournament.query.filter_by(id=tournament_id).first()
    
    if not tournament:
        return jsonify({"detail": "Tournament not found"}), 404
    
    return jsonify(tournament.to_dict()), 200

@tournaments_bp.post("/<int:tournament_id>/participants")
@jwt_required()
def add_participant(tournament_id):
    """Add participant to tournament"""
    tournament = Tournament.query.filter_by(id=tournament_id).first()
    
    if not tournament:
        return jsonify({"detail": "Tournament not found"}), 404
    
    payload = request.get_json(silent=True) or {}
    user_id = payload.get("user_id")
    name = payload.get("name")

    if not name:
        return jsonify({"detail": "Participant name is required"}), 400

    participant = Participant(
        tournament_id=tournament_id,
        user_id=user_id,
        name=name,
    )

    db.session.add(participant)
    db.session.commit()

    return jsonify({"participant": participant.to_dict(), "message": "Participant added"}), 201

@tournaments_bp.get("/<int:tournament_id>/participants")
@jwt_required()
def list_participants(tournament_id):
    """List participants in tournament"""
    tournament = Tournament.query.filter_by(id=tournament_id).first()
    
    if not tournament:
        return jsonify({"detail": "Tournament not found"}), 404
    
    participants = Participant.query.filter_by(tournament_id=tournament_id).all()
    return jsonify([p.to_dict() for p in participants]), 200

@tournaments_bp.put("/<int:tournament_id>/participants")
@jwt_required()
def add_participants_bulk(tournament_id):
    """Add multiple participants to tournament"""
    error = require_trainer_or_admin()
    if error:
        return error
    
    tournament = Tournament.query.filter_by(id=tournament_id).first()
    
    if not tournament:
        return jsonify({"detail": "Tournament not found"}), 404
    
    payload = request.get_json(silent=True) or {}
    participants_data = payload.get("participants", [])
    
    if not participants_data:
        return jsonify({"detail": "No participants provided"}), 400
    
    # Validate participant names
    for p_data in participants_data:
        if not p_data.get("name"):
            return jsonify({"detail": "All participants must have a name"}), 400
    
    # Check max participants limit
    current_count = len(tournament.participants) if tournament.participants else 0
    new_count = current_count + len(participants_data)
    if new_count > tournament.max_participants:
        return jsonify({
            "detail": f"Cannot add {len(participants_data)} participants. Tournament has {current_count}/{tournament.max_participants} participants."
        }), 400
    
    try:
        added_participants = []
        for p_data in participants_data:
            participant = Participant(
                tournament_id=tournament_id,
                user_id=p_data.get("user_id"),
                name=p_data.get("name"),
            )
            db.session.add(participant)
            added_participants.append(participant)
        
        db.session.commit()
        
        return jsonify({
            "message": f"{len(added_participants)} participants added successfully",
            "participants": [p.to_dict() for p in added_participants]
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"detail": f"Failed to add participants: {str(e)}"}), 500

@tournaments_bp.get("/available-users")
@jwt_required()
def get_available_users():
    """Get list of available users (mock endpoint for now)"""
    # This is a placeholder - in a real system, this would query the user service
    # For now, return empty list as users should be in a separate service
    return jsonify({"users": []}), 200

@tournaments_bp.get("/<int:tournament_id>/brackets")
@jwt_required()
def get_brackets(tournament_id):
    """Get tournament brackets"""
    tournament = Tournament.query.filter_by(id=tournament_id).first()
    
    if not tournament:
        return jsonify({"detail": "Tournament not found"}), 404
    
    brackets = Bracket.query.filter_by(tournament_id=tournament_id).order_by(Bracket.round, Bracket.match_number).all()
    return jsonify([b.to_dict() for b in brackets]), 200

@tournaments_bp.get("/<int:tournament_id>/bracket")
@jwt_required()
def get_bracket(tournament_id):
    """Get tournament bracket (alias for /brackets endpoint)"""
    tournament = Tournament.query.filter_by(id=tournament_id).first()
    
    if not tournament:
        return jsonify({"detail": "Tournament not found"}), 404
    
    brackets = Bracket.query.filter_by(tournament_id=tournament_id).order_by(Bracket.round, Bracket.match_number).all()
    participants = Participant.query.filter_by(tournament_id=tournament_id).all()
    
    return jsonify({
        "tournament": tournament.to_dict(),
        "bracket": [b.to_dict() for b in brackets],
        "participants": [p.to_dict() for p in participants]
    }), 200

@tournaments_bp.put("/<int:tournament_id>/bracket/<int:bracket_id>/result")
@jwt_required()
def record_result(tournament_id, bracket_id):
    """Record match result"""
    error = require_trainer_or_admin()
    if error:
        return error
    
    bracket = Bracket.query.filter_by(id=bracket_id, tournament_id=tournament_id).first()
    
    if not bracket:
        return jsonify({"detail": "Match not found"}), 404
    
    # Validate both participants are assigned
    if not bracket.participant1_id or not bracket.participant2_id:
        return jsonify({"detail": "Cannot record result: both participants must be assigned"}), 400
    
    payload = request.get_json(silent=True) or {}
    winner_id = payload.get("winner_id")
    score = payload.get("score")
    
    if not winner_id:
        return jsonify({"detail": "Winner ID is required"}), 400
    
    # Validate winner is one of the participants
    if winner_id not in [bracket.participant1_id, bracket.participant2_id]:
        return jsonify({"detail": "Winner must be one of the match participants"}), 400
    
    try:
        bracket.winner_id = winner_id
        if score:
            bracket.score = score
        
        db.session.commit()
        
        return jsonify({
            "message": "Match result recorded successfully",
            "bracket": bracket.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"detail": f"Failed to record result: {str(e)}"}), 500

@tournaments_bp.get("/health")
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "tournament-service"}), 200
