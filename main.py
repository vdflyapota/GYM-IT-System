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

# --- 1. Register API Routers ---
# These must run FIRST so the API is not blocked by static files
app.include_router(auth.router)
app.include_router(tournaments.router)
app.include_router(challenges.router)
app.include_router(notifications.router)

# --- 2. Explicit Root Route (The Fix) ---
# This forces the server to show index.html when you open the main link
@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

# --- 3. Mount Static Files ---
# This handles all other files like /login.html, /dashboard.html, /css/...
# We name it "static" but mount it to root "/" so URLs look clean.
app.mount("/", StaticFiles(directory="static", html=True), name="static")
