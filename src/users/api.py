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


# ============ Notifications API ============

@users_bp.get("/notifications")
@jwt_required()
def get_notifications():
    """Get user notifications"""
    from flask_jwt_extended import get_jwt_identity
    from src.users.models import Notification
    
    email = get_jwt_identity()
    user = repository.get_by_email(email)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    
    limit = request.args.get("limit", 10, type=int)
    unread_only = request.args.get("unread_only", "false").lower() == "true"
    
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
        "created_at": n.created_at.isoformat() if n.created_at else None
    } for n in notifications]), 200


@users_bp.put("/notifications/<int:notification_id>/read")
@jwt_required()
def mark_notification_read(notification_id):
    """Mark notification as read"""
    from flask_jwt_extended import get_jwt_identity
    from src.users.models import Notification
    from src.common.db import db
    
    email = get_jwt_identity()
    user = repository.get_by_email(email)
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
    from flask_jwt_extended import get_jwt_identity
    from src.users.models import Notification
    from src.common.db import db
    
    email = get_jwt_identity()
    user = repository.get_by_email(email)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    
    notification = Notification.query.filter_by(id=notification_id, user_id=user.id).first()
    
    if not notification:
        return jsonify({"detail": "Notification not found"}), 404
    
    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({"detail": "Notification deleted"}), 200


# ============ Blog API ============

@users_bp.get("/blog/posts")
def get_blog_posts():
    """Get published blog posts (public)"""
    from src.users.models import BlogPost, User
    
    limit = request.args.get("limit", 10, type=int)
    
    posts = BlogPost.query.filter_by(published=True).order_by(
        BlogPost.published_at.desc()
    ).limit(limit).all()
    
    return jsonify([{
        "id": p.id,
        "title": p.title,
        "slug": p.slug,
        "excerpt": p.excerpt,
        "content": p.content,
        "image_url": p.image_url,
        "published_at": p.published_at.isoformat() if p.published_at else None,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "author": {
            "id": p.author.id,
            "full_name": p.author.full_name,
            "email": p.author.email
        } if p.author else None
    } for p in posts]), 200


@users_bp.get("/blog/posts/<slug>")
def get_blog_post(slug):
    """Get single blog post by slug"""
    from src.users.models import BlogPost
    
    post = BlogPost.query.filter_by(slug=slug, published=True).first()
    
    if not post:
        return jsonify({"detail": "Blog post not found"}), 404
    
    return jsonify({
        "id": post.id,
        "title": post.title,
        "slug": post.slug,
        "content": post.content,
        "excerpt": post.excerpt,
        "image_url": post.image_url,
        "published_at": post.published_at.isoformat() if post.published_at else None,
        "created_at": post.created_at.isoformat() if post.created_at else None,
        "author": {
            "id": post.author.id,
            "full_name": post.author.full_name,
            "email": post.author.email
        } if post.author else None
    }), 200


@users_bp.post("/blog/posts")
@jwt_required()
@require_role("admin")
def create_blog_post():
    """Create blog post (admin only)"""
    from flask_jwt_extended import get_jwt_identity
    from src.users.models import BlogPost
    from src.common.db import db
    from datetime import datetime
    import re
    
    email = get_jwt_identity()
    user = repository.get_by_email(email)
    if not user:
        return jsonify({"detail": "User not found"}), 404
    
    data = request.get_json(silent=True) or {}
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    excerpt = data.get("excerpt", "").strip()
    image_url = data.get("image_url", "").strip()
    published = data.get("published", False)
    
    if not title or not content:
        return jsonify({"detail": "Title and content are required"}), 400
    
    # Generate slug from title
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    
    # Ensure unique slug
    existing = BlogPost.query.filter_by(slug=slug).first()
    if existing:
        slug = f"{slug}-{int(datetime.now().timestamp())}"
    
    post = BlogPost(
        title=title,
        slug=slug,
        content=content,
        excerpt=excerpt,
        image_url=image_url,
        author_id=user.id,
        published=published,
        published_at=datetime.now() if published else None
    )
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify({
        "detail": "Blog post created",
        "id": post.id,
        "slug": post.slug
    }), 201


@users_bp.put("/blog/posts/<int:post_id>")
@jwt_required()
@require_role("admin")
def update_blog_post(post_id):
    """Update blog post (admin only)"""
    from src.users.models import BlogPost
    from src.common.db import db
    from datetime import datetime
    
    post = BlogPost.query.get(post_id)
    if not post:
        return jsonify({"detail": "Blog post not found"}), 404
    
    data = request.get_json(silent=True) or {}
    
    if "title" in data:
        post.title = data["title"].strip()
    if "content" in data:
        post.content = data["content"].strip()
    if "excerpt" in data:
        post.excerpt = data["excerpt"].strip()
    if "image_url" in data:
        post.image_url = data["image_url"].strip()
    if "published" in data:
        was_published = post.published
        post.published = data["published"]
        # Set published_at when first published
        if post.published and not was_published:
            post.published_at = datetime.now()
    
    db.session.commit()
    
    return jsonify({"detail": "Blog post updated"}), 200


@users_bp.delete("/blog/posts/<int:post_id>")
@jwt_required()
@require_role("admin")
def delete_blog_post(post_id):
    """Delete blog post (admin only)"""
    from src.users.models import BlogPost
    from src.common.db import db
    
    post = BlogPost.query.get(post_id)
    if not post:
        return jsonify({"detail": "Blog post not found"}), 404
    
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({"detail": "Blog post deleted"}), 200
