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
    Optimized Leaderboard Query - Phase 2 (Yeldana Kadenova)
    - Uses efficient SQL aggregation (handled in database, not Python)
    - Calculates points: Score.value * Challenge.points for accurate scoring
    - Optimized for < 2s latency requirement
    - Returns users even if they have no scores (with 0 points)
    """
    # Optimized query: Join Users, Scores, and Challenges
    # Calculate total points: score_value * challenge_points
    # Use LEFT JOIN to include users with no scores
    results = db.query(
        user_models.User.full_name,
        func.coalesce(
            func.sum(challenge_models.Score.value * challenge_models.Challenge.points),
            0.0
        ).label("total_score")
    ).outerjoin(
        challenge_models.Score, user_models.User.id == challenge_models.Score.user_id
    ).outerjoin(
        challenge_models.Challenge, challenge_models.Score.challenge_id == challenge_models.Challenge.id
    ).group_by(
        user_models.User.id, user_models.User.full_name
    ).order_by(
        func.coalesce(
            func.sum(challenge_models.Score.value * challenge_models.Challenge.points),
            0.0
        ).desc()
    ).all()
    
    # Convert to response format
    return [{"user_name": row[0] or "Unknown", "total_score": float(row[1] or 0)} for row in results]
