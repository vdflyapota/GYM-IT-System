from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

class Tournament(db.Model):
    """Tournament model"""
    __tablename__ = "tournaments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.DateTime(timezone=True), nullable=False)
    max_participants = db.Column(db.Integer, nullable=False)
    tournament_type = db.Column(db.String(50), default="single_elimination", nullable=False)
    status = db.Column(db.String(50), default="setup", nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    participants = db.relationship("Participant", back_populates="tournament", cascade="all, delete-orphan")
    brackets = db.relationship("Bracket", back_populates="tournament", cascade="all, delete-orphan")

    def to_dict(self):
        # Count only approved participants
        # Use getattr to safely handle cases where status column might not exist yet
        try:
            participants_list = self.participants or []
            approved_count = sum(1 for p in participants_list if getattr(p, 'status', 'approved') == "approved")
        except Exception:
            # If there's any issue accessing participants, default to 0
            approved_count = 0
        
        return {
            "id": self.id,
            "name": self.name,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "max_participants": self.max_participants,
            "tournament_type": self.tournament_type,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "participant_count": approved_count,
        }

class Participant(db.Model):
    """Participant model"""
    __tablename__ = "participants"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), nullable=False)
    user_id = db.Column(db.Integer, nullable=True)
    name = db.Column(db.String(255), nullable=False)
    seed = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), default="approved", nullable=False)  # pending, approved
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    tournament = db.relationship("Tournament", back_populates="participants")

    def to_dict(self):
        return {
            "id": self.id,
            "tournament_id": self.tournament_id,
            "user_id": self.user_id,
            "name": self.name,
            "seed": self.seed,
            "status": getattr(self, 'status', 'approved'),  # Default to 'approved' if column doesn't exist
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class Bracket(db.Model):
    """Bracket/Match model"""
    __tablename__ = "brackets"

    id = db.Column(db.Integer, primary_key=True)
    tournament_id = db.Column(db.Integer, db.ForeignKey("tournaments.id"), nullable=False)
    round = db.Column(db.Integer, nullable=False)
    match_number = db.Column(db.Integer, nullable=False)
    participant1_id = db.Column(db.Integer, db.ForeignKey("participants.id"), nullable=True)
    participant2_id = db.Column(db.Integer, db.ForeignKey("participants.id"), nullable=True)
    winner_id = db.Column(db.Integer, db.ForeignKey("participants.id"), nullable=True)
    score = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

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
            "winner_id": self.winner_id,
            "winner": self.winner.to_dict() if self.winner else None,
            "score": self.score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

def init_db(app):
    """Initialize database"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        
        # Migrate existing databases: Add status column to participants if it doesn't exist
        try:
            from sqlalchemy import text, inspect
            
            inspector = inspect(db.engine)
            
            # Check if participants table exists
            if 'participants' in inspector.get_table_names():
                # Get existing columns
                existing_columns = [col['name'] for col in inspector.get_columns('participants')]
                
                # Add status column if it doesn't exist
                if 'status' not in existing_columns:
                    with db.engine.connect() as conn:
                        # Use transaction
                        trans = conn.begin()
                        try:
                            conn.execute(text(
                                "ALTER TABLE participants ADD COLUMN status VARCHAR(50) DEFAULT 'approved' NOT NULL"
                            ))
                            trans.commit()
                            print("✓ Added 'status' column to participants table")
                        except Exception as e:
                            trans.rollback()
                            print(f"Warning: Could not add status column: {e}")
        except Exception as e:
            print(f"Warning: Database migration check failed: {e}")
