from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from .models import db, User
from .config import Config

auth_bp = Blueprint("auth", __name__)

ROLES = ["admin", "trainer", "member"]

@auth_bp.post("/register")
def register():
    """Register a new user - creates user in both auth-service and user-service"""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or "").strip()
    role = (data.get("role") or "member").strip().lower()

    if not email or not password or not full_name:
        return jsonify({"detail": "Missing required fields"}), 400
    if role not in ROLES:
        return jsonify({"detail": "Invalid role"}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"detail": "Email already registered"}), 409

    # Create user in auth database
    user = User(
        email=email,
        password_hash=generate_password_hash(password),
        role=role if role != "admin" else "member",
        is_active=True,
        is_approved=False,
        is_banned=False,
    )
    db.session.add(user)
    db.session.commit()

    # Notify user-service to create user profile
    try:
        user_service_url = Config.USER_SERVICE_URL
        response = requests.post(
            f"{user_service_url}/api/users/create",
            json={
                "user_id": user.id,
                "email": email,
                "full_name": full_name,
                "role": user.role,
                "is_approved": user.is_approved,
            },
            timeout=5
        )
        if response.status_code != 201:
            # Rollback auth user if user-service fails
            db.session.delete(user)
            db.session.commit()
            return jsonify({"detail": "Failed to create user profile"}), 500
    except Exception as e:
        # Rollback on failure
        db.session.delete(user)
        db.session.commit()
        return jsonify({"detail": f"User service unavailable: {str(e)}"}), 503

    return jsonify({
        "detail": "Account created; awaiting admin approval",
        "user": {"email": user.email, "role": user.role, "is_approved": user.is_approved}
    }), 201

@auth_bp.post("/login")
def login():
    """Login and generate JWT token"""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"detail": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"detail": "Invalid credentials"}), 401

    if user.is_banned:
        return jsonify({"detail": "Account is banned"}), 403

    if not user.is_approved:
        return jsonify({"detail": "Account pending approval"}), 403

    if not user.is_active:
        return jsonify({"detail": "Account is inactive"}), 403

    # Create JWT token with user info
    token = create_access_token(
        identity=email,
        additional_claims={
            "user_id": user.id,
            "role": user.role,
        }
    )

    return jsonify({
        "access_token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        }
    }), 200

@auth_bp.post("/validate")
@jwt_required()
def validate_token():
    """Validate JWT token - used by other services"""
    identity = get_jwt_identity()
    user = User.query.filter_by(email=identity).first()
    
    if not user:
        return jsonify({"detail": "User not found"}), 404
    
    return jsonify({
        "valid": True,
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "is_approved": user.is_approved,
        "is_banned": user.is_banned,
    }), 200

@auth_bp.get("/health")
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "auth-service"}), 200

@auth_bp.patch("/sync-approval")
def sync_approval():
    """Sync user approval status from user-service"""
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    is_approved = data.get("is_approved", False)
    
    if not user_id:
        return jsonify({"detail": "user_id required"}), 400
    
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"detail": "User not found"}), 404
    
    user.is_approved = is_approved
    db.session.commit()
    
    return jsonify({"detail": "Approval status synced", "user_id": user_id}), 200

@auth_bp.patch("/sync-ban")
def sync_ban():
    """Sync user ban status from user-service"""
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    is_banned = data.get("is_banned", False)
    
    if not user_id:
        return jsonify({"detail": "user_id required"}), 400
    
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"detail": "User not found"}), 404
    
    user.is_banned = is_banned
    db.session.commit()
    
    return jsonify({"detail": "Ban status synced", "user_id": user_id}), 200
