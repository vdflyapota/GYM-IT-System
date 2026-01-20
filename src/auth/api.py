from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from src.common.db import db
from src.users.models import User
from src.observability.metrics import login_counter
from src.auth.roles import ROLES

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/register")
def register():
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

    # New registrations are not approved by default
    user = User(
        email=email,
        full_name=full_name,
        role=role if role != "admin" else "member",  # prevent self-register as admin
        password_hash=generate_password_hash(password),
        is_active=True,
        is_approved=False,
        is_banned=False,
        is_root_admin=False,
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "detail": "Account created; awaiting admin approval",
        "user": {"email": user.email, "full_name": user.full_name, "role": user.role, "is_approved": user.is_approved}
    }), 201

@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        login_counter.labels(status="failure").inc()
        return jsonify({"detail": "Invalid credentials"}), 401
    if user.is_banned:
        login_counter.labels(status="failure").inc()
        return jsonify({"detail": "Account banned"}), 403
    if not user.is_active:
        login_counter.labels(status="failure").inc()
        return jsonify({"detail": "Inactive account"}), 403
    if not user.is_approved:
        login_counter.labels(status="failure").inc()
        return jsonify({"detail": "Account pending approval"}), 403

    access_token = create_access_token(identity=user.email, additional_claims={"role": user.role})
    login_counter.labels(status="success").inc()
    return jsonify({"access_token": access_token, "token_type": "bearer", "role": user.role}), 200
