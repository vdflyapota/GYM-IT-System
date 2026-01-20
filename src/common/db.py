from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        # Import models so SQLAlchemy knows them before create_all
        from src.users.models import User  # noqa: F401
        db.create_all()
        _ensure_columns(app)
        _ensure_bootstrap_admin(app)

def _ensure_columns(app):
    """
    Lightweight, safe schema adjustments to add approval flags to existing 'users' table.
    Uses IF NOT EXISTS to avoid errors on repeated runs.
    """
    try:
        conn = db.engine.connect()
        conn.exec_driver_sql("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_approved BOOLEAN DEFAULT FALSE NOT NULL;")
        conn.exec_driver_sql("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_banned BOOLEAN DEFAULT FALSE NOT NULL;")
        conn.exec_driver_sql("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_root_admin BOOLEAN DEFAULT FALSE NOT NULL;")
        conn.close()
        app.logger.info("Ensured users approval/root columns exist.")
    except Exception as e:
        app.logger.warning(f"Could not ensure schema columns: {e}")

def _ensure_bootstrap_admin(app):
    import os
    from werkzeug.security import generate_password_hash
    from src.users.models import User

    admin_email = (os.getenv("ADMIN_EMAIL") or "").strip().lower()
    admin_password = (os.getenv("ADMIN_PASSWORD") or "").strip()
    admin_name = (os.getenv("ADMIN_NAME") or "Administrator").strip()
    force_reset = (os.getenv("ADMIN_FORCE_RESET") or "").strip() in {"1", "true", "True"}

    if not admin_email or not admin_password:
        app.logger.info("Bootstrap admin not configured (ADMIN_EMAIL/ADMIN_PASSWORD missing).")
        return

    # Always mark the configured ADMIN_EMAIL user as root admin
    target = User.query.filter_by(email=admin_email).first()
    if target:
        if force_reset:
            target.password_hash = generate_password_hash(admin_password)
            target.is_active = True
            target.is_banned = False
            target.is_approved = True
            target.is_root_admin = True
            db.session.commit()
            app.logger.info(f"Bootstrap admin password updated: {admin_email}")
            return
        else:
            # Ensure root flag and approved for the bootstrap admin
            changed = False
            if not target.is_root_admin:
                target.is_root_admin = True
                changed = True
            if not target.is_approved:
                target.is_approved = True
                changed = True
            if changed:
                db.session.commit()
            app.logger.info("Bootstrap admin email already exists; ensured root/approved flags.")
            return

    any_admin = User.query.filter_by(role="admin").first()
    if any_admin and not force_reset:
        app.logger.info("Admin user already exists; skipping bootstrap.")
        return

    # Create new admin user (auto-approved, root)
    user = User(
        email=admin_email,
        full_name=admin_name,
        role="admin",
        password_hash=generate_password_hash(admin_password),
        is_active=True,
        is_approved=True,
        is_banned=False,
        is_root_admin=True,
    )
    db.session.add(user)
    db.session.commit()
    app.logger.info(f"Bootstrap admin created: {admin_email}")
