"""
Pydantic schemas for Tournament Service API
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# Tournament Schemas
class TournamentCreate(BaseModel):
    name: str
    start_date: datetime
    max_participants: int = 8
    format_type: str = "SINGLE_ELIMINATION"  # SINGLE_ELIMINATION, DOUBLE_ELIMINATION

class TournamentResponse(BaseModel):
    id: int
    name: str
    start_date: datetime
    status: str
    max_participants: int
    format_type: str
    
    class Config:
        from_attributes = True

# Match Schemas
class MatchCreate(BaseModel):
    tournament_id: int
    player1_id: Optional[int] = None
    player2_id: Optional[int] = None
    round_num: int
    match_order: int = 0

class MatchUpdate(BaseModel):
    winner_id: Optional[int] = None
    score_metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class MatchResponse(BaseModel):
    id: int
    tournament_id: int
    player1_id: Optional[int]
    player2_id: Optional[int]
    winner_id: Optional[int]
    round_num: int
    match_order: int
    status: str
    score_metadata: Optional[Dict[str, Any]]
    scheduled_time: Optional[datetime]
    
    class Config:
        from_attributes = True

# Bracket Schemas
class BracketNode(BaseModel):
    match_id: Optional[int]
    player1_id: Optional[int]
    player2_id: Optional[int]
    winner_id: Optional[int]
    round: int
    children: list = []  # For bracket tree structure

class BracketResponse(BaseModel):
    tournament_id: int
    format_type: str
    rounds: list
    matches: list[MatchResponse]
