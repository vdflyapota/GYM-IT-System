from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# --- 1. Register API Routers (Backend Logic) ---
# These MUST come before the static mount so the API takes priority
app.include_router(auth.router)
app.include_router(tournaments.router)
app.include_router(challenges.router)
app.include_router(notifications.router)

# --- 2. Mount Static Files to Root ("/") ---
# This "html=True" setting is magic. 
# It means if you visit "/", it looks for "index.html".
# If you visit "/register.html", it looks for "register.html".
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Note: We removed the manual @app.get("/") because the mount handles it now.
