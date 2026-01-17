from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models.challenge_models import Challenge
from models.user_models import User
from routers.auth import get_current_user, get_current_trainer, get_current_admin

router = APIRouter(prefix="/challenges", tags=["Challenges"])

# --- SCHEMAS ---
class ChallengeCreate(BaseModel):
    title: str
    description: str
    difficulty: str
    points: int

class ChallengeResponse(ChallengeCreate):
    id: int
    created_at: datetime
    is_active: bool  # Send status to frontend
    class Config:
        from_attributes = True

# --- ENDPOINTS ---

@router.get("/", response_model=List[ChallengeResponse])
def get_challenges(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Logic:
    - Members: See ONLY active challenges.
    - Admins: See ALL challenges (so they can approve pending ones).
    """
    if current_user and current_user.role == "admin":
        return db.query(Challenge).all() # Admin sees everything
    
    # Everyone else sees only approved content
    return db.query(Challenge).filter(Challenge.is_active == True).all()

@router.post("/", response_model=ChallengeResponse)
def create_challenge(
    challenge: ChallengeCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_trainer) 
):
    """Trainers create challenges, but they are INACTIVE by default."""
    
    # Auto-approve if the creator is an Admin
    auto_approve = (current_user.role == "admin")
    
    new_challenge = Challenge(
        title=challenge.title,
        description=challenge.description,
        difficulty=challenge.difficulty,
        points=challenge.points,
        created_at=datetime.utcnow(),
        is_active=auto_approve # True if Admin, False if Trainer
    )
    db.add(new_challenge)
    db.commit()
    db.refresh(new_challenge)
    return new_challenge

# --- NEW: APPROVAL ENDPOINT ---
@router.put("/{challenge_id}/approve")
def approve_challenge(
    challenge_id: int, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin) # SECURITY: Admins Only
):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    challenge.is_active = True
    db.commit()
    return {"status": "approved", "title": challenge.title}

# --- NEW: DELETE ENDPOINT (Optional cleanup) ---
@router.delete("/{challenge_id}")
def delete_challenge(
    challenge_id: int, 
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    challenge = db.query(Challenge).filter(Challenge.id == challenge_id).first()
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    db.delete(challenge)
    db.commit()
    return {"status": "deleted"}
