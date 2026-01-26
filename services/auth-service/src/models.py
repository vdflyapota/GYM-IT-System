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
    import requests
    from werkzeug.security import generate_password_hash

    admin_email = (os.getenv("ADMIN_EMAIL") or "").strip().lower()
    admin_password = (os.getenv("ADMIN_PASSWORD") or "").strip()
    admin_name = (os.getenv("ADMIN_NAME") or "Administrator").strip()

    if not admin_email or not admin_password:
        app.logger.info("Bootstrap admin not configured.")
        return

    existing = User.query.filter_by(email=admin_email).first()
    if existing:
        app.logger.info(f"Bootstrap admin already exists: {admin_email}")
        return

    # Create admin in auth database
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
    app.logger.info(f"Bootstrap admin created in auth-service: {admin_email}")
    
    # Also create user profile in user-service
    try:
        user_service_url = os.getenv("USER_SERVICE_URL", "http://user-service:8002")
        response = requests.post(
            f"{user_service_url}/api/users/create",
            json={
                "user_id": user.id,
                "email": admin_email,
                "full_name": admin_name,
                "role": "admin",
                "is_approved": True,
            },
            timeout=5
        )
        if response.status_code == 201:
            app.logger.info(f"Bootstrap admin profile created in user-service: {admin_email}")
        else:
            app.logger.warning(f"Failed to create admin profile in user-service: {response.status_code}")
    except Exception as e:
        app.logger.warning(f"Could not create admin profile in user-service: {e}")
        # Don't fail if user-service is not available, auth still works

