import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "tournament-service-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key")
    
    # Build DATABASE_URL from components for better security
    DB_USER = os.getenv("DB_USER", "tournamentuser")
    DB_PASSWORD = os.getenv("TOURNAMENT_DB_PASSWORD", "tournamentpass")
    DB_HOST = os.getenv("DB_HOST", "tournament-db")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "tournamentdb")
    
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
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
