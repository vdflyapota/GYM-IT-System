from sqlalchemy.sql import func
from src.common.db import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), nullable=False, default="member")  # admin|trainer|member
    password_hash = db.Column(db.String(255), nullable=False)

    # Approval and status flags
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)  # must be True to login
    is_banned = db.Column(db.Boolean, nullable=False, default=False)    # if True, cannot login
    is_root_admin = db.Column(db.Boolean, nullable=False, default=False) # bootstrap/first admin protection

    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
