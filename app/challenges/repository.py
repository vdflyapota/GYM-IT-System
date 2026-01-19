# app/challenges/repository.py
from sqlalchemy.orm import Session
from models.challenge_models import Challenge

class ChallengeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(Challenge).all()

    def get_active(self):
        return self.db.query(Challenge).filter(Challenge.is_active == True).all()

    def create(self, challenge_data, is_active: bool):
        new_challenge = Challenge(
            title=challenge_data.title,
            description=challenge_data.description,
            difficulty=challenge_data.difficulty,
            points=challenge_data.points,
            is_active=is_active
        )
        self.db.add(new_challenge)
        self.db.commit()
        self.db.refresh(new_challenge)
        return new_challenge

    def update_status(self, challenge_id: int, status: bool):
        challenge = self.db.query(Challenge).filter(Challenge.id == challenge_id).first()
        if challenge:
            challenge.is_active = status
            self.db.commit()
        return challenge
