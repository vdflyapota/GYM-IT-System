from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

class User(db.Model):
    """Auth service user model - minimal data for authentication"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), nullable=False, default="member")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    is_banned = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)

def init_db(app):
    """Initialize database"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        _ensure_bootstrap_admin(app)

def _ensure_bootstrap_admin(app):
    """Create bootstrap admin if configured"""
    import os
    from werkzeug.security import generate_password_hash

    admin_email = (os.getenv("ADMIN_EMAIL") or "").strip().lower()
    admin_password = (os.getenv("ADMIN_PASSWORD") or "").strip()

    if not admin_email or not admin_password:
        app.logger.info("Bootstrap admin not configured.")
        return

    existing = User.query.filter_by(email=admin_email).first()
    if existing:
        app.logger.info("Bootstrap admin already exists.")
        return

    user = User(
        email=admin_email,
        password_hash=generate_password_hash(admin_password),
        role="admin",
        is_active=True,
        is_approved=True,
        is_banned=False,
    )
    db.session.add(user)
    db.session.commit()
    app.logger.info(f"Bootstrap admin created: {admin_email}")
