from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime
import uuid

# --- USER SCHEMAS (Yazan) ---
class UserBase(BaseModel):
    email: str
    full_name: str
    role: str = "member"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# --- TOURNAMENT SCHEMAS (Danial) ---
class TournamentCreate(BaseModel):
    name: str
    start_date: datetime
    max_participants: int

class MatchUpdate(BaseModel):
    winner_id: int
    score_metadata: dict  # e.g., {"sets": [11, 9]}

# --- CHALLENGE SCHEMAS (Yeldana) ---
class ChallengeCreate(BaseModel):
    name: str
    metric: str  # "REPS", "TIME"
    points: int

class ScoreSubmit(BaseModel):
    challenge_id: int
    value: float

class LeaderboardEntry(BaseModel):
    user_name: str
    total_score: float

# --- NOTIFICATION SCHEMAS (Shattyk) ---
class NotificationResponse(BaseModel):
    id: int
    message: str
    is_read: bool
    sent_at: datetime
