# models/tournament_models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base

class Tournament(Base):
    __tablename__ = "tournaments"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    start_date = Column(DateTime)
    status = Column(String, default="PENDING") # PENDING, ACTIVE, FINISHED
    
    matches = relationship("Match", back_populates="tournament")

class Match(Base):
    __tablename__ = "matches"
    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    player1_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    player2_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    round_num = Column(Integer)
    score_metadata = Column(JSON, nullable=True)

    tournament = relationship("Tournament", back_populates="matches")
