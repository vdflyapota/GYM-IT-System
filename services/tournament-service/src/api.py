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
        return jsonify({"error": "Tournament name is required"}), 400

    if not start_date:
        return jsonify({"error": "Start date is required"}), 400

    try:
        start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return jsonify({"error": "Invalid start date format"}), 400

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
    return jsonify([t.to_dict() for t in tournaments]), 200

@tournaments_bp.get("/<int:tournament_id>")
@jwt_required()
def get_tournament(tournament_id):
    """Get tournament by ID"""
    tournament = Tournament.query.filter_by(id=tournament_id).first()
    
    if not tournament:
        return jsonify({"error": "Tournament not found"}), 404
    
    return jsonify(tournament.to_dict()), 200

@tournaments_bp.post("/<int:tournament_id>/participants")
@jwt_required()
def add_participant(tournament_id):
    """Add participant to tournament"""
    tournament = Tournament.query.filter_by(id=tournament_id).first()
    
    if not tournament:
        return jsonify({"error": "Tournament not found"}), 404
    
    payload = request.get_json(silent=True) or {}
    user_id = payload.get("user_id")
    name = payload.get("name")

    if not name:
        return jsonify({"error": "Participant name is required"}), 400

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
        return jsonify({"error": "Tournament not found"}), 404
    
    participants = Participant.query.filter_by(tournament_id=tournament_id).all()
    return jsonify([p.to_dict() for p in participants]), 200

@tournaments_bp.get("/<int:tournament_id>/brackets")
@jwt_required()
def get_brackets(tournament_id):
    """Get tournament brackets"""
    tournament = Tournament.query.filter_by(id=tournament_id).first()
    
    if not tournament:
        return jsonify({"error": "Tournament not found"}), 404
    
    brackets = Bracket.query.filter_by(tournament_id=tournament_id).order_by(Bracket.round, Bracket.match_number).all()
    return jsonify([b.to_dict() for b in brackets]), 200

@tournaments_bp.get("/health")
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "tournament-service"}), 200
