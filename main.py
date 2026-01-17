from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from jose import jwt, JWTError
from database import engine, Base
# Import all models to ensure tables are created in the DB
from models import user_models, tournament_models, challenge_models, notification_models
# Import routers
from routers import auth, tournaments, challenges, notifications
# Import Security Keys from auth to verify tokens in main.py
# (Ensure SECRET_KEY and ALGORITHM are available in routers/auth.py)
from routers.auth import SECRET_KEY, ALGORITHM

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


# --- 2. SECURE ADMIN ROUTE (The Vault) ---
# This endpoint replaces the direct file access.
# It acts as a security guard for the Admin Panel.
@app.get("/admin") 
async def read_admin_panel(request: Request):
    # 1. Get the cookie set by the Login endpoint
    token_header = request.cookies.get("access_token")
    
    # 2. If no cookie, they are definitely not logged in -> Kick them out
    if not token_header:
        return RedirectResponse(url="/login.html")
    
    try:
        # 3. Clean the token (Remove "Bearer " prefix if present)
        scheme, _, param = token_header.partition(" ")
        token = param if scheme.lower() == "bearer" else token_header
        
        # 4. Verify the Digital Signature
        # If a hacker faked the cookie, this line will crash (raise JWTError)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        
        if not email:
            return RedirectResponse(url="/login.html")
            
        # (Optional: You could also query the DB here to check if role == 'admin' 
        # to prevent even "Members" from seeing the HTML structure)

    except JWTError:
        # Token is expired or fake -> Kick them out
        return RedirectResponse(url="/login.html")

    # 5. Success! The user is authenticated. Open the vault.
    return FileResponse("templates/admin.html")


# --- 3. Explicit Root Route ---
# Forces the server to serve the Landing Page at "/"
@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

# --- 4. Mount Static Files ---
# Handles all public files (images, css, js, login.html, etc.)
# Note: "admin.html" is NO LONGER here, so the public cannot reach it.
# --- Explicit Routes for Critical Pages ---
# This forces the server to find these specific files
@app.get("/register.html")
async def read_register():
    return FileResponse("static/register.html")

@app.get("/login.html")
async def read_login():
    return FileResponse("static/login.html")

@app.get("/dashboard.html")
async def read_dashboard():
    return FileResponse("static/dashboard.html")

# --- Mount Static Files (Keep this at the very end) ---
app.mount("/", StaticFiles(directory="static", html=True), name="static")
