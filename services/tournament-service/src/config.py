import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "tournament-service-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://tournamentuser:tournamentpass@tournament-db:5432/tournamentdb",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
    ENV = os.getenv("ENV", "development")
    DEBUG = ENV == "development"
    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")]
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600"))
    
    # Service discovery
    USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user-service:8002")
    NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8004")
