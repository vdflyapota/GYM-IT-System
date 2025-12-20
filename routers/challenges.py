# routers/challenges.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, aliased
from sqlalchemy import func
from database import get_db
from models import challenge_models, user_models
import schemas

router = APIRouter(prefix="/challenges", tags=["Challenges & Leaderboards"])

@router.post("/create")
def create_challenge(c: schemas.ChallengeCreate, db: Session = Depends(get_db)):
    new_challenge = challenge_models.Challenge(name=c.name, metric=c.metric, points=c.points)
    db.add(new_challenge)
    db.commit()
    return {"status": "Challenge Created"}

@router.post("/submit-score")
def submit_score(s: schemas.ScoreSubmit, user_id: int = 1, db: Session = Depends(get_db)):
    # Note: user_id=1 is hardcoded for simplicity until Auth is fully linked
    new_score = challenge_models.Score(
        user_id=user_id, 
        challenge_id=s.challenge_id, 
        value=s.value
    )
    db.add(new_score)
    db.commit()
    return {"status": "Score Recorded"}

@router.get("/leaderboard", response_model=list[schemas.LeaderboardEntry])
def get_leaderboard(db: Session = Depends(get_db)):
    """
    Complex Query: Sums points for each user to create a ranking.
    Demonstrates 'Responsiveness' (Aggregation handled in SQL, not Python)
    """
    # Join Users and Scores, sum the points
    results = db.query(
        user_models.User.full_name,
        func.sum(challenge_models.Score.value).label("total_score")
    ).join(challenge_models.Score).group_by(user_models.User.id).order_by(func.sum(challenge_models.Score.value).desc()).all()
    
    return [{"user_name": row[0], "total_score": row[1]} for row in results]
