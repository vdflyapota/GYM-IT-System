import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "api-gateway-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")
    ENV = os.getenv("ENV", "development")
    DEBUG = ENV == "development"
    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]
    
    # Service URLs
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001")
    USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8002")
    TOURNAMENT_SERVICE_URL = os.getenv("TOURNAMENT_SERVICE_URL", "http://tournament-service:8003")
    NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8004")
