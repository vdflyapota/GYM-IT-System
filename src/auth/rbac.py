from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt
from werkzeug.exceptions import Forbidden

def require_role(*allowed_roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            role = claims.get("role")
            if role not in allowed_roles:
                raise Forbidden("Insufficient role")
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def add_rbac_error_handlers(app):
    @app.errorhandler(Forbidden)
    def handle_forbidden(e):
        return jsonify({"message": str(e)}), 403
