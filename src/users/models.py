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


class Notification(db.Model):
    __tablename__ = "notifications"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False, default='info')  # info, success, warning, error
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    link = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    user = db.relationship('User', backref='notifications')


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    published = db.Column(db.Boolean, nullable=False, default=False)
    published_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=True, onupdate=func.now())
    
    author = db.relationship('User', backref='blog_posts')
