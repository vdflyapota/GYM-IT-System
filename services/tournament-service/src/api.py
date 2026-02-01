from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from datetime import datetime
from .models import db, Tournament, Participant, Bracket
import logging
import requests

tournaments_bp = Blueprint("tournaments", __name__)

def get_current_user_role():
    """Helper to get current user role from JWT"""
    claims = get_jwt()
    return claims.get("role", "member")

def get_current_user_id():
    """Helper to get current user ID from JWT"""
    claims = get_jwt()
    return claims.get("user_id")

def require_trainer_or_admin():
    """Helper to check if current user is trainer or admin"""
    role = get_current_user_role()
    if role not in ["trainer", "admin"]:
        return jsonify({"detail": "Trainer or Admin access required"}), 403
    return None

def require_admin():
    """Helper to check if current user is admin"""
    role = get_current_user_role()
    if role != "admin":
        return jsonify({"detail": "Admin access required"}), 403
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
    registration_deadline = payload.get("registration_deadline")  # Optional
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

    # Parse and validate registration_deadline if provided
    deadline_dt = None
    if registration_deadline and registration_deadline.strip():  # Check for non-empty string
        try:
            deadline_dt = datetime.fromisoformat(registration_deadline.replace("Z", "+00:00"))
            
            # Validate deadline is in the future
            if deadline_dt <= datetime.now(deadline_dt.tzinfo):
                return jsonify({"detail": "Registration deadline must be in the future"}), 400
            
            # Validate deadline is before start date
            if deadline_dt >= start_dt:
                return jsonify({"detail": "Registration deadline must be before tournament start date"}), 400
                
        except (ValueError, AttributeError):
            return jsonify({"detail": "Invalid registration deadline format"}), 400

    try:
        tournament = Tournament(
            name=name,
            start_date=start_dt,
            registration_deadline=deadline_dt,
            max_participants=max_participants,
            tournament_type=tournament_type,
            status="setup",
        )

        db.session.add(tournament)
        db.session.commit()

        return jsonify({"tournament": tournament.to_dict(), "message": "Tournament created successfully"}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating tournament: {str(e)}")
        return jsonify({"detail": f"Failed to create tournament: {str(e)}"}), 500

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

@tournaments_bp.delete("/<int:tournament_id>")
@jwt_required()
def delete_tournament(tournament_id):
    """Delete a tournament - admin or trainer only"""
    error = require_trainer_or_admin()
    if error:
        return error
    
    tournament = Tournament.query.filter_by(id=tournament_id).first()
    
    if not tournament:
        return jsonify({"detail": "Tournament not found"}), 404
    
    try:
        # Cascade delete will automatically remove participants and brackets
        db.session.delete(tournament)
        db.session.commit()
        
        return jsonify({"message": "Tournament deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting tournament: {str(e)}")
        return jsonify({"detail": f"Failed to delete tournament: {str(e)}"}), 500

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
    """Add multiple participants to tournament
    
    Trainers/admins can add any participants (approved by default).
    Members can request to join (creates pending participant).
    """
    role = get_current_user_role()
    current_user_id = get_current_user_id()
    
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
    
    # Determine status based on role
    participant_status = "approved"  # Default for trainers/admins
    
    # Check authorization based on role
    if role == "member":
        # Members can only add themselves
        if len(participants_data) > 1:
            return jsonify({"detail": "Members can only add themselves to tournaments"}), 403
        
        participant_data = participants_data[0]
        participant_user_id = participant_data.get("user_id")
        
        # Verify they're adding themselves
        if participant_user_id and str(participant_user_id) != str(current_user_id):
            return jsonify({"detail": "Members can only add themselves to tournaments"}), 403
        
        # Members create pending requests
        participant_status = "pending"
    elif role not in ["trainer", "admin"]:
        return jsonify({"detail": "Unauthorized to add participants"}), 403
    
    # Check max participants limit (only count approved participants)
    approved_count = Participant.query.filter_by(
        tournament_id=tournament_id,
        status="approved"
    ).count()
    new_count = approved_count + len(participants_data)
    if new_count > tournament.max_participants and participant_status == "approved":
        return jsonify({
            "detail": f"Cannot add {len(participants_data)} participants. Tournament has {approved_count}/{tournament.max_participants} participants."
        }), 400
    
    try:
        added_participants = []
        for p_data in participants_data:
            # Check if user is already a participant (pending or approved)
            user_id = p_data.get("user_id")
            if user_id:
                existing = Participant.query.filter_by(
                    tournament_id=tournament_id,
                    user_id=user_id
                ).first()
                if existing:
                    if existing.status == "pending":
                        return jsonify({"detail": f"You already have a pending request for this tournament"}), 400
                    else:
                        return jsonify({"detail": f"User is already a participant in this tournament"}), 400
            
            participant = Participant(
                tournament_id=tournament_id,
                user_id=p_data.get("user_id"),
                name=p_data.get("name"),
                status=participant_status,
            )
            db.session.add(participant)
            added_participants.append(participant)
        
        db.session.commit()
        
        if participant_status == "pending":
            return jsonify({
                "message": "Join request submitted successfully! Waiting for trainer/admin approval.",
                "participants": [p.to_dict() for p in added_participants]
            }), 200
        else:
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
    """Get list of available users from user-service"""
    from .config import Config
    
    # Only trainers and admins can see available users
    error = require_trainer_or_admin()
    if error:
        return error
    
    try:
        # Fetch users from user-service
        user_service_url = Config.USER_SERVICE_URL
        
        # Get the JWT token from the current request
        from flask import request as flask_request
        auth_header = flask_request.headers.get('Authorization', '')
        
        response = requests.get(
            f"{user_service_url}/api/users/",
            headers={'Authorization': auth_header},
            timeout=5
        )
        
        if response.status_code == 200:
            users_data = response.json()
            # Transform user data to match expected format
            users = [
                {
                    "id": user.get("id"),
                    "name": user.get("full_name") or user.get("email"),
                    "email": user.get("email")
                }
                for user in users_data
                if user.get("is_approved") and not user.get("is_banned")
            ]
            return jsonify({"users": users}), 200
        else:
            # Return empty list if user-service fails
            return jsonify({"users": []}), 200
            
    except Exception as e:
        # Log error but return empty list to not break the UI
        logging.error(f"Error fetching users from user-service: {str(e)}")
        return jsonify({"users": []}), 200

@tournaments_bp.patch("/<int:tournament_id>/participants/<int:participant_id>/approve")
@jwt_required()
def approve_participant(tournament_id, participant_id):
    """Approve a pending participant - trainer or admin only"""
    error = require_trainer_or_admin()
    if error:
        return error
    
    tournament = Tournament.query.filter_by(id=tournament_id).first()
    if not tournament:
        return jsonify({"detail": "Tournament not found"}), 404
    
    participant = Participant.query.filter_by(
        id=participant_id,
        tournament_id=tournament_id
    ).first()
    
    if not participant:
        return jsonify({"detail": "Participant not found"}), 404
    
    if participant.status != "pending":
        return jsonify({"detail": "Participant is not pending approval"}), 400
    
    # Check if tournament is full
    approved_count = Participant.query.filter_by(
        tournament_id=tournament_id,
        status="approved"
    ).count()
    
    if approved_count >= tournament.max_participants:
        return jsonify({"detail": "Tournament is full"}), 400
    
    participant.status = "approved"
    db.session.commit()
    
    return jsonify({
        "message": "Participant approved successfully",
        "participant": participant.to_dict()
    }), 200

@tournaments_bp.post("/<int:tournament_id>/generate-bracket")
@jwt_required()
def generate_bracket(tournament_id):
    """Generate tournament bracket - trainer or admin only"""
    error = require_trainer_or_admin()
    if error:
        return error
    
    tournament = Tournament.query.filter_by(id=tournament_id).first()
    if not tournament:
        return jsonify({"detail": "Tournament not found"}), 404
    
    # Get approved participants only
    participants = Participant.query.filter_by(
        tournament_id=tournament_id,
        status="approved"
    ).all()
    
    if len(participants) < 2:
        return jsonify({"detail": "Need at least 2 approved participants to generate bracket"}), 400
    
    # Delete existing brackets
    Bracket.query.filter_by(tournament_id=tournament_id).delete()
    
    # Simple single elimination bracket generation
    import math
    num_participants = len(participants)
    
    # Assign seeds
    for idx, participant in enumerate(participants):
        participant.seed = idx + 1
    
    # Calculate number of rounds needed
    num_rounds = math.ceil(math.log2(num_participants))
    
    # First round matchups
    matches_first_round = []
    for i in range(0, len(participants), 2):
        p1 = participants[i] if i < len(participants) else None
        p2 = participants[i + 1] if (i + 1) < len(participants) else None
        
        bracket = Bracket(
            tournament_id=tournament_id,
            round=1,
            match_number=len(matches_first_round) + 1,
            participant1_id=p1.id if p1 else None,
            participant2_id=p2.id if p2 else None,
        )
        db.session.add(bracket)
        matches_first_round.append(bracket)
    
    # Create placeholder matches for subsequent rounds
    current_round_matches = matches_first_round
    for round_num in range(2, num_rounds + 1):
        next_round_matches = []
        for i in range(0, len(current_round_matches), 2):
            bracket = Bracket(
                tournament_id=tournament_id,
                round=round_num,
                match_number=len(next_round_matches) + 1,
            )
            db.session.add(bracket)
            next_round_matches.append(bracket)
        current_round_matches = next_round_matches
    
    tournament.status = "active"
    db.session.commit()
    
    return jsonify({
        "message": "Bracket generated successfully",
        "rounds": num_rounds,
        "matches": len(matches_first_round)
    }), 200

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
    
    tournament = Tournament.query.filter_by(id=tournament_id).first()
    if not tournament:
        return jsonify({"detail": "Tournament not found"}), 404
    
    bracket = Bracket.query.filter_by(id=bracket_id, tournament_id=tournament_id).first()
    
    if not bracket:
        return jsonify({"detail": "Match not found"}), 404
    
    # Validate both participants are assigned
    if not bracket.participant1_id or not bracket.participant2_id:
        return jsonify({"detail": "Cannot record result: both participants must be assigned"}), 400
    
    payload = request.get_json(silent=True) or {}
    winner_id = payload.get("winner_id")
    score = payload.get("score", "")
    
    if not winner_id:
        return jsonify({"detail": "winner_id is required"}), 400
    
    # Validate winner is one of the participants
    if winner_id not in [bracket.participant1_id, bracket.participant2_id]:
        return jsonify({"detail": "Winner must be one of the match participants"}), 400
    
    bracket.winner_id = winner_id
    bracket.score = score
    
    # Advance winner to next round
    next_round = bracket.round + 1
    next_match_number = (bracket.match_number + 1) // 2
    
    next_bracket = Bracket.query.filter_by(
        tournament_id=tournament_id,
        round=next_round,
        match_number=next_match_number
    ).first()
    
    if next_bracket:
        # Determine which slot to fill (participant1 or participant2)
        if bracket.match_number % 2 == 1:
            next_bracket.participant1_id = winner_id
        else:
            next_bracket.participant2_id = winner_id
    
    db.session.commit()
    
    # Check if this was the final match
    final_round_matches = Bracket.query.filter_by(tournament_id=tournament_id).all()
    if final_round_matches:
        max_round = max(m.round for m in final_round_matches)
        final_match = Bracket.query.filter_by(
            tournament_id=tournament_id,
            round=max_round
        ).first()
        
        if final_match and final_match.winner_id:
            tournament.status = "completed"
            db.session.commit()
    
    return jsonify({
        "message": "Match result recorded successfully",
        "bracket": bracket.to_dict()
    }), 200
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

@tournaments_bp.patch("/<int:tournament_id>/pause")
@jwt_required()
def pause_tournament(tournament_id):
    """Pause a tournament - admin only"""
    error = require_admin()
    if error:
        return error
    
    tournament = Tournament.query.filter_by(id=tournament_id).first()
    if not tournament:
        return jsonify({"detail": "Tournament not found"}), 404
    
    # Don't allow pausing completed tournaments
    if tournament.status == "completed":
        return jsonify({"detail": "Cannot pause a completed tournament"}), 400
    
    try:
        tournament.is_paused = True
        db.session.commit()
        logging.info(f"Tournament {tournament_id} paused by admin")
        return jsonify({"message": "Tournament paused successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error pausing tournament: {str(e)}")
        return jsonify({"detail": f"Failed to pause tournament: {str(e)}"}), 500

@tournaments_bp.patch("/<int:tournament_id>/resume")
@jwt_required()
def resume_tournament(tournament_id):
    """Resume a paused tournament - admin only"""
    
    error = require_admin()
    if error:
        return error
    
    tournament = Tournament.query.filter_by(id=tournament_id).first()
    if not tournament:
        return jsonify({"detail": "Tournament not found"}), 404
    
    try:
        tournament.is_paused = False
        db.session.commit()
        logging.info(f"Tournament {tournament_id} resumed by admin")
        return jsonify({"message": "Tournament resumed successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error resuming tournament: {str(e)}")
        return jsonify({"detail": f"Failed to resume tournament: {str(e)}"}), 500

@tournaments_bp.delete("/<int:tournament_id>/bracket/<int:bracket_id>/result")
@jwt_required()
def clear_result(tournament_id, bracket_id):
    """Clear a match result - admin only"""
    
    error = require_admin()
    if error:
        return error
    
    tournament = Tournament.query.filter_by(id=tournament_id).first()
    if not tournament:
        return jsonify({"detail": "Tournament not found"}), 404
    
    bracket = Bracket.query.filter_by(id=bracket_id, tournament_id=tournament_id).first()
    if not bracket:
        return jsonify({"detail": "Match not found"}), 404
    
    try:
        # If this match had a winner who advanced to next round, clear them from next round
        if bracket.winner_id:
            # Find next round match where this winner was placed
            next_round_matches = Bracket.query.filter_by(
                tournament_id=tournament_id,
                round=bracket.round + 1
            ).all()
            
            for next_match in next_round_matches:
                if next_match.participant1_id == bracket.winner_id:
                    next_match.participant1_id = None
                    logging.info(f"Cleared participant1 from match {next_match.id}")
                elif next_match.participant2_id == bracket.winner_id:
                    next_match.participant2_id = None
                    logging.info(f"Cleared participant2 from match {next_match.id}")
        
        # Clear the result
        bracket.winner_id = None
        bracket.score = None
        
        db.session.commit()
        logging.info(f"Match result cleared for bracket {bracket_id} in tournament {tournament_id}")
        return jsonify({"message": "Match result cleared successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error clearing result: {str(e)}")
        return jsonify({"detail": f"Failed to clear result: {str(e)}"}), 500

@tournaments_bp.get("/health")
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "tournament-service"}), 200
