from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import engine, Base

# Import all models to ensure tables are created
from models import user_models, tournament_models, challenge_models, notification_models

# Import routers
from routers import auth, tournaments, challenges, notifications

# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HealthGYM System",
    description="Architecture Course Project - Team 4",
    version="1.0.0"
)

# --- 1. Register API Routers (Backend Logic) ---
app.include_router(auth.router)
app.include_router(tournaments.router)
app.include_router(challenges.router)
app.include_router(notifications.router)

# --- 2. THE FIX: Explicitly Serve the Homepage ---
# This tells the server: "When user goes to '/', give them index.html"
@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

# --- 3. Mount Static Files ---
# This handles css, images, and other html files (like login.html)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
