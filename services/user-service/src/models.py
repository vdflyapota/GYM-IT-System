from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """User service user model - extended profile information"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)  # Same ID as auth-service
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), nullable=False, default="member")
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_banned = db.Column(db.Boolean, nullable=False, default=False)
    is_root_admin = db.Column(db.Boolean, nullable=False, default=False)
    bio = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Notification(db.Model):
    """User notifications"""
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
    """Blog posts"""
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
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    author = db.relationship('User', backref='blog_posts')

class PasswordResetToken(db.Model):
    """Password reset tokens"""
    __tablename__ = "password_reset_tokens"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    used = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    user = db.relationship('User', backref='reset_tokens')

def init_db(app):
    """Initialize database"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
