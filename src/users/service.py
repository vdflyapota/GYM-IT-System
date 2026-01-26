from werkzeug.security import generate_password_hash
from .models import User
from . import repository


def create_admin(email: str, full_name: str, password: str) -> User:
    user = User(
        email=email,
        full_name=full_name,
        role="admin",
        password_hash=generate_password_hash(password),
        is_active=True,
        is_approved=True,
        is_banned=False,
        is_root_admin=False,
    )
    return repository.save(user)


def change_role(user: User, new_role: str) -> User:
    user.role = new_role
    repository.commit()
    return user


def approve_user(user: User) -> User:
    user.is_approved = True
    user.is_active = True
    user.is_banned = False
    repository.commit()
    return user


def deactivate_user(user: User) -> User:
    user.is_active = False
    repository.commit()
    return user


def ban_user(user: User) -> User:
    user.is_banned = True
    user.is_active = False
    repository.commit()
    return user


def unban_user(user: User) -> User:
    user.is_banned = False
    repository.commit()
    return user


def reset_password(user: User, new_password: str) -> User:
    user.password_hash = generate_password_hash(new_password)
    repository.commit()
    return user
