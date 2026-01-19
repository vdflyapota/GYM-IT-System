# routers/challenges.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from routers.auth import get_current_user, get_current_trainer, get_current_admin
from models.user_models import User

# Import the new layers
from app.challenges.repository import ChallengeRepository
from app.challenges.service import ChallengeService
from pydantic import BaseModel

router = APIRouter(prefix="/challenges", tags=["Challenges"])

# --- SCHEMAS (Keep your Pydantic models here or move to schemas.py) ---
class ChallengeCreate(BaseModel):
    title: str
    description: str
    difficulty: str
    points: int

# --- DEPENDENCY INJECTION HELPER ---
def get_service(db: Session = Depends(get_db)):
    repo = ChallengeRepository(db)
    return ChallengeService(repo)

# --- ENDPOINTS ---

@router.get("/")
def get_challenges(
    service: ChallengeService = Depends(get_service),
    current_user: User = Depends(get_current_user)
):
    return service.get_challenges_for_user(current_user)

@router.post("/")
def create_challenge(
    data: ChallengeCreate, 
    service: ChallengeService = Depends(get_service),
    current_user: User = Depends(get_current_trainer)
):
    return service.create_challenge(data, current_user)

@router.put("/{id}/approve")
def approve_challenge(
    id: int, 
    service: ChallengeService = Depends(get_service),
    admin: User = Depends(get_current_admin)
):
    result = service.approve_challenge(id)
    if not result:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return {"status": "approved"}
