"""
Tournament Models for Tournament Service
Note: player_id references users in auth-service (will be validated via API call)
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base

class Tournament(Base):
    __tablename__ = "tournaments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    status = Column(String, default="PENDING")  # PENDING, ACTIVE, FINISHED
    max_participants = Column(Integer, default=8)
    format_type = Column(String, default="SINGLE_ELIMINATION")  # SINGLE_ELIMINATION, DOUBLE_ELIMINATION
    
    matches = relationship("Match", back_populates="tournament", cascade="all, delete-orphan")

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=False)
    
    # Player IDs reference users in auth-service (will be validated via API)
    player1_id = Column(Integer, nullable=True)
    player2_id = Column(Integer, nullable=True)
    winner_id = Column(Integer, nullable=True)
    
    round_num = Column(Integer, nullable=False)
    match_order = Column(Integer, default=0)  # Order within the round
    status = Column(String, default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED
    score_metadata = Column(JSON, nullable=True)  # e.g., {"sets": [11, 9], "duration": 120}
    scheduled_time = Column(DateTime, nullable=True)
    
    tournament = relationship("Tournament", back_populates="matches")
