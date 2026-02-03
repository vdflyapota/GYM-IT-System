from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.common.db import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), nullable=False, default="member")  # admin|trainer|member
    password_hash = db.Column(db.String(255), nullable=False)

    # Optional profile fields
    phone = db.Column(db.String(64), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    avatar_url = db.Column(db.String(512), nullable=True)

    # Approval and status flags
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)  # must be True to login
    is_banned = db.Column(db.Boolean, nullable=False, default=False)    # if True, cannot login
    is_root_admin = db.Column(db.Boolean, nullable=False, default=False) # bootstrap/first admin protection

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    notifications = relationship("Notification", back_populates="user", order_by="Notification.created_at.desc()")


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(32), nullable=False, default="info")  # info|success|warning|error
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="notifications")


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
