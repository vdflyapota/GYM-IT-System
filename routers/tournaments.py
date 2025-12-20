# routers/tournaments.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import tournament_models, user_models
import schemas

router = APIRouter(prefix="/tournaments", tags=["Tournament Engine"])

@router.post("/", response_model=dict)
def create_tournament(t: schemas.TournamentCreate, db: Session = Depends(get_db)):
    new_tourney = tournament_models.Tournament(
        name=t.name, 
        start_date=t.start_date
    )
    db.add(new_tourney)
    db.commit()
    db.refresh(new_tourney)
    return {"status": "created", "id": new_tourney.id}

@router.post("/{id}/generate-bracket")
def generate_bracket(id: int, db: Session = Depends(get_db)):
    """Simple algorithm to pair up all users in the DB"""
    users = db.query(user_models.User).limit(8).all() # Grab first 8 users
    
    matches_created = []
    # Create pairs (1 vs 2, 3 vs 4, etc.)
    for i in range(0, len(users), 2):
        if i+1 < len(users):
            match = tournament_models.Match(
                tournament_id=id,
                player1_id=users[i].id,
                player2_id=users[i+1].id,
                round_num=1
            )
            db.add(match)
            matches_created.append(f"{users[i].full_name} vs {users[i+1].full_name}")
    
    db.commit()
    return {"message": "Bracket generated", "matches": matches_created}
