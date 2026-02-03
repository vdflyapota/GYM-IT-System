from flask import Blueprint, request, jsonify, current_app as app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import requests
from .models import db, User
from .config import Config

users_bp = Blueprint("users", __name__)

def get_current_user_role():
    """Helper to get current user role from JWT"""
    claims = get_jwt()
    return claims.get("role", "member")

def require_admin():
    """Helper to check if current user is admin"""
    role = get_current_user_role()
    if role != "admin":
        return jsonify({"detail": "Admin access required"}), 403
    return None

def require_admin_or_trainer():
    """Helper to check if current user is admin or trainer"""
    role = get_current_user_role()
    if role not in ["admin", "trainer"]:
        return jsonify({"detail": "Admin or Trainer access required"}), 403
    return None

@users_bp.post("/create")
def create_user():
    """Create user profile - called by auth-service after registration"""
    data = request.get_json(silent=True) or {}
    
    user_id = data.get("user_id")
    email = data.get("email")
    full_name = data.get("full_name")
    role = data.get("role", "member")
    is_approved = data.get("is_approved", False)

    if not user_id or not email or not full_name:
        return jsonify({"detail": "Missing required fields"}), 400

    existing = User.query.filter_by(id=user_id).first()
    if existing:
        return jsonify({"detail": "User already exists"}), 409

    user = User(
        id=user_id,
        email=email,
        full_name=full_name,
        role=role,
        is_approved=is_approved,
        is_banned=False,
        is_root_admin=False,
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"detail": "User profile created", "user_id": user.id}), 201

@users_bp.get("/me")
@jwt_required()
def get_me():
    """Get current user profile"""
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({"detail": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_approved": user.is_approved,
        "is_banned": user.is_banned,
        "is_root_admin": user.is_root_admin,
    }), 200

@users_bp.get("/")
@jwt_required()
def list_users():
    """List all users - admin or trainer"""
    error = require_admin_or_trainer()
    if error:
        return error
    
    users = User.query.all()
    return jsonify([
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_approved": u.is_approved,
            "is_banned": u.is_banned,
            "is_root_admin": u.is_root_admin,
        }
        for u in users
    ]), 200

@users_bp.get("/<int:user_id>")
@jwt_required()
def get_user(user_id):
    """Get user by ID"""
    user = User.query.filter_by(id=user_id).first()
    
    if not user:
        return jsonify({"detail": "User not found"}), 404
    
    return jsonify({
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_approved": user.is_approved,
        "is_banned": user.is_banned,
    }), 200

@users_bp.patch("/approve")
@jwt_required()
def approve_user():
    """Approve a user - admin only"""
    error = require_admin()
    if error:
        return error
    
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    
    if not user_id:
        return jsonify({"detail": "user_id required"}), 400
    
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"detail": "User not found"}), 404
    
    user.is_approved = True
    db.session.commit()
    
    # Notify auth-service to update approval status
    try:
        auth_service_url = Config.AUTH_SERVICE_URL
        response = requests.patch(
            f"{auth_service_url}/api/auth/sync-approval",
            json={"user_id": user_id, "is_approved": True},
            timeout=5
        )
        if response.status_code != 200:
            app.logger.warning(f"Failed to sync approval to auth-service: {response.text}")
    except Exception as e:
        app.logger.warning(f"Auth service sync failed: {str(e)}")
    
    return jsonify({"detail": "User approved", "user_id": user.id}), 200

@users_bp.patch("/ban")
@jwt_required()
def ban_user():
    """Ban a user - admin only"""
    error = require_admin()
    if error:
        return error
    
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    
    if not user_id:
        return jsonify({"detail": "user_id required"}), 400
    
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"detail": "User not found"}), 404
    
    # Prevent banning root admin
    if user.is_root_admin:
        return jsonify({"detail": "Cannot ban root admin user"}), 403
    
    user.is_banned = True
    db.session.commit()
    
    # Notify auth-service to update ban status
    try:
        auth_service_url = Config.AUTH_SERVICE_URL
        response = requests.patch(
            f"{auth_service_url}/api/auth/sync-ban",
            json={"user_id": user_id, "is_banned": True},
            timeout=5
        )
        if response.status_code != 200:
            app.logger.warning(f"Failed to sync ban to auth-service: {response.text}")
    except Exception as e:
        app.logger.warning(f"Auth service sync failed: {str(e)}")
    
    return jsonify({"detail": "User banned", "user_id": user.id}), 200

@users_bp.delete("/<int:user_id>")
@jwt_required()
def delete_user(user_id):
    """Delete a user - admin only"""
    error = require_admin()
    if error:
        return error
    
    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"detail": "User not found"}), 404
    
    # Prevent deleting root admin
    if user.is_root_admin:
        return jsonify({"detail": "Cannot delete root admin user"}), 403
    
    # Delete the user
    db.session.delete(user)
    db.session.commit()
    
    # Notify auth-service to delete the auth record
    try:
        auth_service_url = Config.AUTH_SERVICE_URL
        response = requests.delete(
            f"{auth_service_url}/api/auth/user/{user_id}",
            timeout=5
        )
        if response.status_code not in [200, 204, 404]:
            app.logger.warning(f"Failed to delete from auth-service: {response.text}")
    except Exception as e:
        app.logger.warning(f"Auth service sync failed: {str(e)}")
    
    return jsonify({"detail": "User deleted"}), 200

@users_bp.get("/reports/statistics")
@jwt_required()
def get_user_statistics():
    """Get user statistics for reports - admin only"""
    error = require_admin()
    if error:
        return error
    
    from datetime import datetime, timedelta
    from sqlalchemy import func, extract
    
    # Get query parameters for filtering
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    role_filter = request.args.get('role')
    
    # Base query
    query = User.query
    
    # Apply date filters if provided
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(User.created_at >= start_dt)
        except ValueError:
            pass
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(User.created_at <= end_dt)
        except ValueError:
            pass
    
    # Apply role filter if provided
    if role_filter and role_filter != 'all':
        query = query.filter(User.role == role_filter)
    
    # Get all users matching filters
    users = query.all()
    
    # Calculate statistics
    total_users = len(users)
    
    # Count by role
    role_counts = db.session.query(
        User.role,
        func.count(User.id)
    ).group_by(User.role).all()
    
    by_role = {role: count for role, count in role_counts}
    
    # Count by approval status
    approved_count = User.query.filter_by(is_approved=True).count()
    pending_count = User.query.filter_by(is_approved=False).count()
    
    # Count by ban status
    banned_count = User.query.filter_by(is_banned=True).count()
    active_count = total_users - banned_count
    
    # Get registration trend (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_users = User.query.filter(User.created_at >= thirty_days_ago).all()
    
    # Group by date
    registrations_by_date = {}
    for user in recent_users:
        date_key = user.created_at.strftime('%Y-%m-%d')
        registrations_by_date[date_key] = registrations_by_date.get(date_key, 0) + 1
    
    # Get detailed user list
    user_list = []
    for u in users:
        user_list.append({
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_approved": u.is_approved,
            "is_banned": u.is_banned,
            "is_root_admin": u.is_root_admin,
            "created_at": u.created_at.isoformat() if u.created_at else None
        })
    
    return jsonify({
        "total_users": total_users,
        "by_role": by_role,
        "approved_users": approved_count,
        "pending_users": pending_count,
        "active_users": active_count,
        "banned_users": banned_count,
        "registrations_by_date": registrations_by_date,
        "users": user_list
    }), 200

@users_bp.get("/health")
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "user-service"}), 200
