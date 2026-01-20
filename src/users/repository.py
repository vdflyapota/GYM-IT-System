from typing import Optional, List
from src.common.db import db
from .models import User


def get_by_email(email: str) -> Optional[User]:
    return User.query.filter_by(email=email).first()


def get_by_id(user_id: int) -> Optional[User]:
    return User.query.get(user_id)


def list_all() -> List[User]:
    return User.query.all()


def save(user: User) -> User:
    db.session.add(user)
    db.session.commit()
    return user


def delete(user: User) -> None:
    db.session.delete(user)
    db.session.commit()


def commit() -> None:
    db.session.commit()
