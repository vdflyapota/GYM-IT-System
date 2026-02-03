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

# ==========================================
# PROFILE MANAGEMENT ENDPOINTS
# ==========================================

@users_bp.put("/me")
@jwt_required()
def update_profile():
    """Update current user profile"""
    from .models import User, db
    
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({"detail": "User not found"}), 404
    
    data = request.get_json(silent=True) or {}
    
    # Update allowed fields
    if "full_name" in data:
        user.full_name = data["full_name"]
    if "bio" in data:
        user.bio = data["bio"]
    if "phone" in data:
        user.phone = data["phone"]
    if "avatar_url" in data:
        user.avatar_url = data["avatar_url"]
    
    db.session.commit()
    
    return jsonify({
        "detail": "Profile updated successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "bio": user.bio,
            "phone": user.phone,
            "avatar_url": user.avatar_url,
            "role": user.role
        }
    }), 200

# ==========================================
# NOTIFICATION ENDPOINTS
# ==========================================

@users_bp.get("/notifications")
@jwt_required()
def get_notifications():
    """Get user notifications"""
    from .models import Notification, User
    
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({"detail": "User not found"}), 404
    
    # Get query parameters
    limit = request.args.get('limit', 50, type=int)
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    
    query = Notification.query.filter_by(user_id=user.id)
    
    if unread_only:
        query = query.filter_by(is_read=False)
    
    notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    return jsonify([{
        "id": n.id,
        "title": n.title,
        "message": n.message,
        "type": n.type,
        "is_read": n.is_read,
        "link": n.link,
        "created_at": n.created_at.isoformat()
    } for n in notifications]), 200

@users_bp.post("/notifications")
@jwt_required()
def create_notification():
    """Create notification (admin only)"""
    from .models import Notification, User, db
    
    error = require_admin()
    if error:
        return error
    
    data = request.get_json(silent=True) or {}
    
    user_id = data.get("user_id")
    title = data.get("title")
    message = data.get("message")
    notification_type = data.get("type", "info")
    link = data.get("link")
    
    if not user_id or not title or not message:
        return jsonify({"detail": "Missing required fields"}), 400
    
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notification_type,
        link=link
    )
    
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({"detail": "Notification created", "id": notification.id}), 201

@users_bp.put("/notifications/<int:notification_id>/read")
@jwt_required()
def mark_notification_read(notification_id):
    """Mark notification as read"""
    from .models import Notification, User, db
    
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({"detail": "User not found"}), 404
    
    notification = Notification.query.filter_by(id=notification_id, user_id=user.id).first()
    
    if not notification:
        return jsonify({"detail": "Notification not found"}), 404
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({"detail": "Notification marked as read"}), 200

@users_bp.delete("/notifications/<int:notification_id>")
@jwt_required()
def delete_notification(notification_id):
    """Delete notification"""
    from .models import Notification, User, db
    
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({"detail": "User not found"}), 404
    
    notification = Notification.query.filter_by(id=notification_id, user_id=user.id).first()
    
    if not notification:
        return jsonify({"detail": "Notification not found"}), 404
    
    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({"detail": "Notification deleted"}), 200

# ==========================================
# BLOG ENDPOINTS
# ==========================================

@users_bp.get("/blog/posts")
def get_blog_posts():
    """Get published blog posts (public)"""
    from .models import BlogPost, User
    
    limit = request.args.get('limit', 10, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    posts = BlogPost.query.filter_by(published=True).order_by(BlogPost.published_at.desc()).limit(limit).offset(offset).all()
    
    return jsonify([{
        "id": p.id,
        "title": p.title,
        "slug": p.slug,
        "excerpt": p.excerpt,
        "content": p.content,
        "author": {
            "id": p.author.id,
            "full_name": p.author.full_name
        } if p.author else None,
        "image_url": p.image_url,
        "published_at": p.published_at.isoformat() if p.published_at else None,
        "created_at": p.created_at.isoformat()
    } for p in posts]), 200

@users_bp.get("/blog/posts/<slug>")
def get_blog_post(slug):
    """Get single blog post by slug"""
    from .models import BlogPost
    
    post = BlogPost.query.filter_by(slug=slug, published=True).first()
    
    if not post:
        return jsonify({"detail": "Blog post not found"}), 404
    
    return jsonify({
        "id": post.id,
        "title": post.title,
        "slug": post.slug,
        "content": post.content,
        "excerpt": post.excerpt,
        "author": {
            "id": post.author.id,
            "full_name": post.author.full_name,
            "avatar_url": post.author.avatar_url
        } if post.author else None,
        "image_url": post.image_url,
        "published_at": post.published_at.isoformat() if post.published_at else None,
        "created_at": post.created_at.isoformat()
    }), 200

@users_bp.post("/blog/posts")
@jwt_required()
def create_blog_post():
    """Create blog post (admin/trainer only)"""
    from .models import BlogPost, User, db
    from datetime import datetime
    
    error = require_admin_or_trainer()
    if error:
        return error
    
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({"detail": "User not found"}), 404
    
    data = request.get_json(silent=True) or {}
    
    title = data.get("title")
    content = data.get("content")
    excerpt = data.get("excerpt")
    image_url = data.get("image_url")
    published = data.get("published", False)
    
    if not title or not content:
        return jsonify({"detail": "Title and content are required"}), 400
    
    # Create slug from title
    import re
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    
    # Make slug unique
    base_slug = slug
    counter = 1
    while BlogPost.query.filter_by(slug=slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    post = BlogPost(
        title=title,
        slug=slug,
        content=content,
        excerpt=excerpt or content[:200],
        author_id=user.id,
        image_url=image_url,
        published=published,
        published_at=datetime.utcnow() if published else None
    )
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify({"detail": "Blog post created", "id": post.id, "slug": post.slug}), 201

@users_bp.put("/blog/posts/<int:post_id>")
@jwt_required()
def update_blog_post(post_id):
    """Update blog post (admin/trainer only)"""
    from .models import BlogPost, User, db
    from datetime import datetime
    
    error = require_admin_or_trainer()
    if error:
        return error
    
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({"detail": "User not found"}), 404
    
    post = BlogPost.query.get(post_id)
    
    if not post:
        return jsonify({"detail": "Blog post not found"}), 404
    
    # Only author or admin can update
    if post.author_id != user.id and user.role != "admin":
        return jsonify({"detail": "Not authorized to update this post"}), 403
    
    data = request.get_json(silent=True) or {}
    
    if "title" in data:
        post.title = data["title"]
    if "content" in data:
        post.content = data["content"]
    if "excerpt" in data:
        post.excerpt = data["excerpt"]
    if "image_url" in data:
        post.image_url = data["image_url"]
    if "published" in data:
        was_published = post.published
        post.published = data["published"]
        # Set published_at when first publishing
        if not was_published and post.published:
            post.published_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({"detail": "Blog post updated"}), 200

@users_bp.delete("/blog/posts/<int:post_id>")
@jwt_required()
def delete_blog_post(post_id):
    """Delete blog post (admin/trainer only)"""
    from .models import BlogPost, User, db
    
    error = require_admin_or_trainer()
    if error:
        return error
    
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({"detail": "User not found"}), 404
    
    post = BlogPost.query.get(post_id)
    
    if not post:
        return jsonify({"detail": "Blog post not found"}), 404
    
    # Only author or admin can delete
    if post.author_id != user.id and user.role != "admin":
        return jsonify({"detail": "Not authorized to delete this post"}), 403
    
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({"detail": "Blog post deleted"}), 200

# ==========================================
# PASSWORD RESET ENDPOINTS
# ==========================================

@users_bp.post("/password/reset-request")
def request_password_reset():
    """Request password reset token"""
    from .models import User, PasswordResetToken, db
    from datetime import datetime, timedelta
    import secrets
    
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    
    if not email:
        return jsonify({"detail": "Email is required"}), 400
    
    user = User.query.filter_by(email=email).first()
    
    # Always return success to prevent email enumeration
    if not user:
        return jsonify({"detail": "If the email exists, a reset link will be sent"}), 200
    
    # Generate token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)
    
    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    
    db.session.add(reset_token)
    db.session.commit()
    
    # In production, send email here
    # For now, just return the token (in production, this would be in email only)
    return jsonify({
        "detail": "If the email exists, a reset link will be sent",
        "token": token  # Remove this in production
    }), 200

@users_bp.post("/password/reset")
def reset_password():
    """Reset password with token"""
    from .models import User, PasswordResetToken, db
    from datetime import datetime
    import requests
    
    data = request.get_json(silent=True) or {}
    token = data.get("token")
    new_password = data.get("new_password")
    
    if not token or not new_password:
        return jsonify({"detail": "Token and new password are required"}), 400
    
    reset_token = PasswordResetToken.query.filter_by(token=token, used=False).first()
    
    if not reset_token:
        return jsonify({"detail": "Invalid or expired token"}), 400
    
    if datetime.utcnow() > reset_token.expires_at:
        return jsonify({"detail": "Token has expired"}), 400
    
    # Call auth service to update password
    auth_service_url = Config.AUTH_SERVICE_URL
    try:
        response = requests.post(
            f"{auth_service_url}/update-password",
            json={
                "user_id": reset_token.user_id,
                "new_password": new_password
            }
        )
        
        if response.status_code != 200:
            return jsonify({"detail": "Failed to update password"}), 500
    except Exception as e:
        return jsonify({"detail": f"Failed to contact auth service: {str(e)}"}), 500
    
    # Mark token as used
    reset_token.used = True
    db.session.commit()
    
    return jsonify({"detail": "Password reset successfully"}), 200
