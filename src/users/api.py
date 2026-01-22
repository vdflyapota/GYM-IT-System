from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from src.auth.rbac import require_role
from src.users.models import User
from src.users import repository, service

users_bp = Blueprint("users", __name__)

def _protect_root(user: User):
    return bool(user and user.is_root_admin)

def _parse_user_id(data):
    raw = data.get("user_id")
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None

@users_bp.get("/me")
@jwt_required()
def me():
    from flask_jwt_extended import get_jwt_identity
    email = get_jwt_identity()
    user = repository.get_by_email(email)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "is_approved": user.is_approved,
        "is_banned": user.is_banned,
        "is_root_admin": user.is_root_admin,
    })

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
