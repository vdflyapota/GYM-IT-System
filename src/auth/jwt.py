from flask_jwt_extended import JWTManager

def init_jwt(app):
    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {"message": "Token has expired"}, 401

    @jwt.unauthorized_loader
    def missing_token_callback(err):
        return {"message": "Missing or invalid token"}, 401
