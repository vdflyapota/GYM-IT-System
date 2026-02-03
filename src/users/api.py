from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.auth.rbac import require_role
from src.users.models import User, Notification, PasswordResetToken
from src.users import repository, service
from src.common.db import db
from src.notifications.events import emit_new_notification

users_bp = Blueprint("users", __name__)

def _protect_root(user: User):
    return bool(user and user.is_root_admin)

def _parse_user_id(data):
    raw = data.get("user_id")
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None

def _user_to_me_dict(user: User):
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "phone": getattr(user, "phone", None),
        "bio": getattr(user, "bio", None),
        "avatar_url": getattr(user, "avatar_url", None),
        "is_active": user.is_active,
        "is_approved": user.is_approved,
        "is_banned": user.is_banned,
        "is_root_admin": user.is_root_admin,
    }


@users_bp.get("/me")
@jwt_required()
def me():
    email = get_jwt_identity()
    user = repository.get_by_email(email)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    return jsonify(_user_to_me_dict(user))


@users_bp.put("/me")
@jwt_required()
def update_me():
    """Update current user profile (full_name, phone, bio, avatar_url)."""
    email = get_jwt_identity()
    user = repository.get_by_email(email)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    data = request.get_json(silent=True) or {}
    if "full_name" in data and data["full_name"] is not None:
        user.full_name = (data["full_name"] or "").strip() or user.full_name
    if "phone" in data:
        user.phone = (data["phone"] or "").strip() or None
    if "bio" in data:
        user.bio = (data["bio"] or "").strip() or None
    if "avatar_url" in data:
        user.avatar_url = (data["avatar_url"] or "").strip() or None
    repository.commit()
    return jsonify(_user_to_me_dict(user)), 200


@users_bp.get("/notifications")
@jwt_required()
def list_notifications():
    """List notifications for current user, optional ?limit=10."""
    email = get_jwt_identity()
    user = repository.get_by_email(email)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    limit = min(int(request.args.get("limit", 20)), 50)
    notifications = (
        Notification.query.filter_by(user_id=user.id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )
    return jsonify([
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "type": n.type,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in notifications
    ])


@users_bp.put("/notifications/<int:notification_id>/read")
@jwt_required()
def mark_notification_read(notification_id):
    """Mark a notification as read (only own)."""
    email = get_jwt_identity()
    user = repository.get_by_email(email)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    notif = Notification.query.filter_by(id=notification_id, user_id=user.id).first()
    if not notif:
        return jsonify({"detail": "Notification not found"}), 404
    notif.is_read = True
    db.session.commit()
    return jsonify({"detail": "OK"}), 200


@users_bp.post("/me/change_password")
@jwt_required()
def change_password_me():
    """Change password for current user. Body: { current_password, new_password }."""
    from werkzeug.security import check_password_hash, generate_password_hash
    email = get_jwt_identity()
    user = repository.get_by_email(email)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    data = request.get_json(silent=True) or {}
    current = data.get("current_password") or ""
    new_password = data.get("new_password") or ""
    if not current or not new_password:
        return jsonify({"detail": "current_password and new_password are required"}), 400
    if not check_password_hash(user.password_hash, current):
        return jsonify({"detail": "Current password is incorrect"}), 401
    if len(new_password) < 6:
        return jsonify({"detail": "New password must be at least 6 characters"}), 400
    user.password_hash = generate_password_hash(new_password)
    repository.commit()
    return jsonify({"detail": "Password updated"}), 200


@users_bp.post("/password/reset-request")
def password_reset_request():
    """Request password reset. Body: { email }. Returns token in dev for demo (no email sent)."""
    from werkzeug.security import generate_password_hash
    from datetime import datetime, timedelta
    import secrets
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    if not email:
        return jsonify({"detail": "email is required"}), 400
    user = repository.get_by_email(email)
    if not user:
        return jsonify({"detail": "If this email exists, you will receive a reset link shortly."}), 200
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)
    PasswordResetToken.query.filter_by(user_id=user.id).delete()
    db.session.add(PasswordResetToken(user_id=user.id, token=token, expires_at=expires_at))
    db.session.commit()
    # In production: send email with link containing token. For demo, return token.
    return jsonify({"detail": "If this email exists, you will receive a reset link shortly.", "token": token}), 200


@users_bp.post("/password/reset")
def password_reset():
    """Reset password with token. Body: { token, new_password }."""
    from werkzeug.security import generate_password_hash
    from datetime import datetime
    data = request.get_json(silent=True) or {}
    token = (data.get("token") or "").strip()
    new_password = data.get("new_password") or ""
    if not token or not new_password:
        return jsonify({"detail": "token and new_password are required"}), 400
    if len(new_password) < 6:
        return jsonify({"detail": "Password must be at least 6 characters"}), 400
    row = PasswordResetToken.query.filter_by(token=token).first()
    if not row or row.expires_at < datetime.utcnow():
        return jsonify({"detail": "Invalid or expired token"}), 400
    user = repository.get_by_id(row.user_id)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    user.password_hash = generate_password_hash(new_password)
    db.session.delete(row)
    db.session.commit()
    return jsonify({"detail": "Password reset successfully"}), 200


@users_bp.get("/")
@jwt_required()
@require_role("admin")
def list_users():
    users = repository.list_all()
    return jsonify([
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "is_approved": u.is_approved,
            "is_banned": u.is_banned,
            "is_root_admin": u.is_root_admin,
        } for u in users
    ])

@users_bp.post("/create_admin")
@jwt_required()
@require_role("admin")
def create_admin():
    """
    Admin-only creation of another admin user.
    Body: { "email": str, "full_name": str, "password": str }
    Newly created admin is approved and active.
    """
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    full_name = (data.get("full_name") or "").strip()
    password = data.get("password") or ""

    if not email or not password or not full_name:
        return jsonify({"detail": "Missing required fields"}), 400
    if repository.get_by_email(email):
        return jsonify({"detail": "Email already exists"}), 409
    user = service.create_admin(email=email, full_name=full_name, password=password)
    return jsonify({"detail": "Admin created", "user_id": user.id}), 201

@users_bp.patch("/role")
@jwt_required()
@require_role("admin")
def change_role():
    data = request.get_json(silent=True) or {}
    user_id = _parse_user_id(data)
    new_role = (data.get("role") or "").lower()
    if not user_id:
        return jsonify({"detail": "user_id is required"}), 400
    if new_role not in {"admin", "trainer", "member"}:
        return jsonify({"detail": "Invalid role"}), 400
    user = repository.get_by_id(user_id)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    if _protect_root(user):
        return jsonify({"detail": "Operation not permitted on the root admin"}), 403
    user = service.change_role(user, new_role)
    return jsonify({"detail": "Role updated", "user": {"id": user.id, "email": user.email, "role": user.role}}), 200

@users_bp.post("/approve")
@jwt_required()
@require_role("admin")
def approve_user():
    data = request.get_json(silent=True) or {}
    user_id = _parse_user_id(data)
    if not user_id:
        return jsonify({"detail": "user_id is required"}), 400
    user = repository.get_by_id(user_id)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    # approving root or others is fine
    service.approve_user(user)
    return jsonify({"detail": "User approved"}), 200

@users_bp.post("/deactivate")
@jwt_required()
@require_role("admin")
def deactivate_user():
    data = request.get_json(silent=True) or {}
    user_id = _parse_user_id(data)
    if not user_id:
        return jsonify({"detail": "user_id is required"}), 400
    user = repository.get_by_id(user_id)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    if _protect_root(user):
        return jsonify({"detail": "Operation not permitted on the root admin"}), 403
    service.deactivate_user(user)
    return jsonify({"detail": "User deactivated"}), 200

@users_bp.post("/ban")
@jwt_required()
@require_role("admin")
def ban_user():
    data = request.get_json(silent=True) or {}
    user_id = _parse_user_id(data)
    if not user_id:
        return jsonify({"detail": "user_id is required"}), 400
    user = repository.get_by_id(user_id)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    if _protect_root(user):
        return jsonify({"detail": "Operation not permitted on the root admin"}), 403
    service.ban_user(user)
    return jsonify({"detail": "User banned"}), 200

@users_bp.post("/unban")
@jwt_required()
@require_role("admin")
def unban_user():
    data = request.get_json(silent=True) or {}
    user_id = _parse_user_id(data)
    if not user_id:
        return jsonify({"detail": "user_id is required"}), 400
    user = repository.get_by_id(user_id)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    service.unban_user(user)
    return jsonify({"detail": "User unbanned"}), 200

@users_bp.delete("/<int:user_id>")
@jwt_required()
@require_role("admin")
def delete_user(user_id: int):
    user = repository.get_by_id(user_id)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    if _protect_root(user):
        return jsonify({"detail": "Operation not permitted on the root admin"}), 403
    repository.delete(user)
    return jsonify({"detail": "User deleted"}), 200

@users_bp.post("/reset_password")
@jwt_required()
@require_role("admin")
def reset_password():
    """
    Admin-only password reset endpoint.
    Body: { "user_id": int, "new_password": str }
    """
    data = request.get_json(silent=True) or {}
    user_id = _parse_user_id(data)
    new_password = data.get("new_password") or ""
    if not user_id or not new_password:
        return jsonify({"detail": "user_id and new_password are required"}), 400
    user = repository.get_by_id(user_id)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    if _protect_root(user):
        return jsonify({"detail": "Operation not permitted on the root admin"}), 403
    service.reset_password(user, new_password)
    return jsonify({"detail": "Password updated"}), 200
