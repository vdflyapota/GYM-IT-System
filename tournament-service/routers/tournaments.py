"""
Tournament API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import tournament_models
from schemas import (
    TournamentCreate, TournamentResponse,
    MatchCreate, MatchUpdate, MatchResponse,
    BracketResponse
)

router = APIRouter(prefix="/tournaments", tags=["Tournaments"])

@router.post("/", response_model=TournamentResponse, status_code=status.HTTP_201_CREATED)
def create_tournament(tournament: TournamentCreate, db: Session = Depends(get_db)):
    """Create a new tournament"""
    new_tournament = tournament_models.Tournament(
        name=tournament.name,
        start_date=tournament.start_date,
        max_participants=tournament.max_participants,
        format_type=tournament.format_type
    )
    db.add(new_tournament)
    db.commit()
    db.refresh(new_tournament)
    return new_tournament

@router.get("/", response_model=List[TournamentResponse])
def list_tournaments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all tournaments"""
    tournaments = db.query(tournament_models.Tournament).offset(skip).limit(limit).all()
    return tournaments

@router.get("/{tournament_id}", response_model=TournamentResponse)
def get_tournament(tournament_id: int, db: Session = Depends(get_db)):
    """Get tournament by ID"""
    tournament = db.query(tournament_models.Tournament).filter(
        tournament_models.Tournament.id == tournament_id
    ).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament

@router.post("/{tournament_id}/generate-bracket", response_model=dict)
def generate_bracket(tournament_id: int, participant_ids: List[int], db: Session = Depends(get_db)):
    """
    Generate bracket for tournament with given participants
    Note: participant_ids should be validated against auth-service
    """
    tournament = db.query(tournament_models.Tournament).filter(
        tournament_models.Tournament.id == tournament_id
    ).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    # Simple single elimination bracket generation
    matches_created = []
    round_num = 1
    current_participants = participant_ids.copy()
    
    # Handle odd number of participants (bye for last one)
    if len(current_participants) % 2 != 0:
        current_participants.append(None)  # Bye
    
    match_order = 0
    while len(current_participants) > 1:
        next_round_participants = []
        
        for i in range(0, len(current_participants), 2):
            player1_id = current_participants[i]
            player2_id = current_participants[i + 1] if i + 1 < len(current_participants) else None
            
            match = tournament_models.Match(
                tournament_id=tournament_id,
                player1_id=player1_id,
                player2_id=player2_id,
                round_num=round_num,
                match_order=match_order,
                status="PENDING"
            )
            db.add(match)
            db.flush()  # Get match ID
            
            matches_created.append({
                "match_id": match.id,
                "round": round_num,
                "player1_id": player1_id,
                "player2_id": player2_id
            })
            
            # Winner advances (placeholder - will be set when match is completed)
            next_round_participants.append(player1_id)  # Temporary, will be winner_id
            match_order += 1
        
        current_participants = next_round_participants
        round_num += 1
        match_order = 0
    
    db.commit()
    return {
        "message": "Bracket generated successfully",
        "tournament_id": tournament_id,
        "matches_created": len(matches_created),
        "matches": matches_created
    }

@router.get("/{tournament_id}/bracket", response_model=BracketResponse)
def get_bracket(tournament_id: int, db: Session = Depends(get_db)):
    """Get tournament bracket with all matches"""
    tournament = db.query(tournament_models.Tournament).filter(
        tournament_models.Tournament.id == tournament_id
    ).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    matches = db.query(tournament_models.Match).filter(
        tournament_models.Match.tournament_id == tournament_id
    ).order_by(tournament_models.Match.round_num, tournament_models.Match.match_order).all()
    
    # Group matches by round
    rounds = {}
    for match in matches:
        if match.round_num not in rounds:
            rounds[match.round_num] = []
        rounds[match.round_num].append(MatchResponse.model_validate(match))
    
    return BracketResponse(
        tournament_id=tournament_id,
        format_type=tournament.format_type,
        rounds=list(rounds.keys()),
        matches=[MatchResponse.model_validate(m) for m in matches]
    )

@router.put("/matches/{match_id}", response_model=MatchResponse)
def update_match(match_id: int, match_update: MatchUpdate, db: Session = Depends(get_db)):
    """Update match score and winner"""
    match = db.query(tournament_models.Match).filter(
        tournament_models.Match.id == match_id
    ).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    if match_update.winner_id is not None:
        match.winner_id = match_update.winner_id
        match.status = "COMPLETED"
    
    if match_update.score_metadata is not None:
        match.score_metadata = match_update.score_metadata
    
    if match_update.status is not None:
        match.status = match_update.status
    
    db.commit()
    db.refresh(match)
    return match

@router.get("/matches/{match_id}", response_model=MatchResponse)
def get_match(match_id: int, db: Session = Depends(get_db)):
    """Get match by ID"""
    match = db.query(tournament_models.Match).filter(
        tournament_models.Match.id == match_id
    ).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match
