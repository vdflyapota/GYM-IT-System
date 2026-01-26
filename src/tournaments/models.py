from sqlalchemy.sql import func
from src.common.db import db


class Tournament(db.Model):
    __tablename__ = "tournaments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.DateTime(timezone=True), nullable=False)
    max_participants = db.Column(db.Integer, nullable=False)
    tournament_type = db.Column(db.String(50), default="single_elimination", nullable=False)
    status = db.Column(db.String(50), default="setup", nullable=False)  # setup, active, completed
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    participants = db.relationship("Participant", back_populates="tournament", cascade="all, delete-orphan")
    brackets = db.relationship("Bracket", back_populates="tournament", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "max_participants": self.max_participants,
            "tournament_type": self.tournament_type,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "participant_count": len(self.participants) if self.participants else 0,
        }


class Participant(db.Model):
    __tablename__ = "participants"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # Optional link to user
    name = db.Column(db.String(255), nullable=False)
    seed = db.Column(db.Integer, nullable=True)  # Seeding for bracket generation
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    tournament = db.relationship("Tournament", back_populates="participants")
    user = db.relationship("User", foreign_keys=[user_id])

    def to_dict(self):
        result = {
            "id": self.id,
            "tournament_id": self.tournament_id,
            "user_id": self.user_id,
            "name": self.name,
            "seed": self.seed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
        # Include user email if linked to a user
        if self.user:
            result["email"] = self.user.email
        return result


class Bracket(db.Model):
    __tablename__ = "brackets"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), nullable=False)
    round = db.Column(db.Integer, nullable=False)  # 1 for first round, 2 for second, etc.
    match_number = db.Column(db.Integer, nullable=False)  # Match number within the round
    participant1_id = db.Column(db.Integer, db.ForeignKey("participants.id"), nullable=True)
    participant2_id = db.Column(db.Integer, db.ForeignKey("participants.id"), nullable=True)
    winner_id = db.Column(db.Integer, db.ForeignKey("participants.id"), nullable=True)
    score = db.Column(db.String(50), nullable=True)  # e.g., "3-2", "2-1"
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    tournament = db.relationship("Tournament", back_populates="brackets")
    participant1 = db.relationship("Participant", foreign_keys=[participant1_id])
    participant2 = db.relationship("Participant", foreign_keys=[participant2_id])
    winner = db.relationship("Participant", foreign_keys=[winner_id])

    def to_dict(self):
        return {
            "id": self.id,
            "tournament_id": self.tournament_id,
            "round": self.round,
            "match_number": self.match_number,
            "participant1": self.participant1.to_dict() if self.participant1 else None,
            "participant2": self.participant2.to_dict() if self.participant2 else None,
            "winner": self.winner.to_dict() if self.winner else None,
            "score": self.score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
