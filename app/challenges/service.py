# app/challenges/service.py
from app.challenges.repository import ChallengeRepository
from models.user_models import User

class ChallengeService:
    def __init__(self, repo: ChallengeRepository):
        self.repo = repo

    def get_challenges_for_user(self, user: User):
        # RULE: Admins see everything (to audit), Members see only Active
        if user.role == "admin":
            return self.repo.get_all()
        return self.repo.get_active()

    def create_challenge(self, data, user: User):
        # RULE: Admins publish instantly. Trainers need approval.
        auto_approve = (user.role == "admin")
        return self.repo.create(data, is_active=auto_approve)

    def approve_challenge(self, challenge_id: int):
        return self.repo.update_status(challenge_id, True)
