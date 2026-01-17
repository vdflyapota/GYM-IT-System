from sqlalchemy import Column, Integer, String, DateTime, Boolean
from database import Base
from datetime import datetime

class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    difficulty = Column(String)
    points = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # NEW: Status Flag
    is_active = Column(Boolean, default=False)
