from fastapi import FastAPI
from database import engine, Base

# Import all models
from models import user_models, tournament_models, challenge_models, notification_models

# Import routers
from routers import auth, tournaments, challenges, notifications

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HealthGYM System",
    description="Architecture Course Project - Team 4",
    version="1.0.0"
)

# --- API root: one UI is the React frontend (see README) ---
@app.get("/")
def root():
    return {
        "message": "HealthGYM API",
        "docs": "/docs",
        "frontend": "http://localhost:3000 (run: cd frontend && npm run dev)",
    }

# --- Register API Routers ---
app.include_router(auth.router)
app.include_router(tournaments.router)
app.include_router(challenges.router)
app.include_router(notifications.router)
