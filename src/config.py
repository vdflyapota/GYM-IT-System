import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-too")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://gymit:gymit@db:5432/gymit"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
    # Security at rest
    AES256_KEY_BASE64 = os.getenv("AES256_KEY_BASE64")  # 32-byte key, base64-encoded
    # Backups
    BACKUP_BUCKET = os.getenv("BACKUP_BUCKET", "")
    BACKUP_ENC_RECIPIENT = os.getenv("BACKUP_ENC_RECIPIENT", "")
    # Environment
    ENV = os.getenv("ENV", "development")
