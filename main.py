import time
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from jose import jwt, JWTError
from database import engine, Base

# --- IMPORTS: MODELS ---
# We import these so SQLAlchemy creates the tables automatically
from models import user_models, tournament_models, challenge_models, notification_models

# --- IMPORTS: ROUTERS ---
from routers import auth, tournaments, challenges, notifications

# --- IMPORTS: SECURITY KEYS ---
# Needed to verify the Admin Cookie
from routers.auth import SECRET_KEY, ALGORITHM

# --- 1. INITIALIZE DATABASE ---
# This creates the file 'gym.db' if it doesn't exist
Base.metadata.create_all(bind=engine)

# --- 2. APP DEFINITION ---
app = FastAPI(
    title="HealthGYM System",
    description="Architecture Course Project - Team 4",
    version="1.2.0"
)

# --- 3. ARCHITECTURE: RESPONSIVENESS (Middleware) ---
# Measures how long every request takes. 
# Satisfies "Responsiveness" requirement (logging slow requests).
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    # Calculate duration
    process_time = time.time() - start_time
    
    # Add header for debugging/monitoring
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log slow requests (> 1 second) for "Scalability" analysis
    if process_time > 1.0:
        print(f"⚠️ SLOW REQUEST: {request.url} took {process_time:.4f}s")
        
    return response

# --- 4. ARCHITECTURE: FAULT TOLERANCE (Exception Handler) ---
# Prevents the server from crashing completely on unexpected errors.
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"🔥 CRITICAL ERROR: {exc}") # Log for Admin
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal System Error. The technical team has been notified."}
    )

# --- 5. REGISTER ROUTERS (The Modules) ---
app.include_router(auth.router)
app.include_router(tournaments.router)
app.include_router(challenges.router)
app.include_router(notifications.router)


# --- 6. HEALTH CHECK (For Architecture/Kubernetes) ---
@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected", "version": "1.2.0"}


# --- 7. SECURE ADMIN VAULT (The "Cookie" Protection) ---
# Intercepts requests to /admin and checks for a valid secure cookie.
@app.get("/admin") 
async def read_admin_panel(request: Request):
    token_header = request.cookies.get("access_token")
    
    if not token_header:
        return RedirectResponse(url="/login.html")
    
    try:
        # Clean token
        scheme, _, param = token_header.partition(" ")
        token = param if scheme.lower() == "bearer" else token_header
        
        # Verify Signature
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # If successful, serve the protected file
        return FileResponse("templates/admin.html")

    except JWTError:
        return RedirectResponse(url="/login.html")


# --- 8. EXPLICIT ROUTES FOR STATIC PAGES ---
# Prevents "Not Found" errors by manually mapping these URLs
@app.get("/register.html")
async def read_register(): return FileResponse("static/register.html")

@app.get("/login.html")
async def read_login(): return FileResponse("static/login.html")

@app.get("/dashboard.html")
async def read_dashboard(): return FileResponse("static/dashboard.html")

@app.get("/challenges.html")
async def read_challenges(): return FileResponse("static/challenges.html")


# --- 9. ROOT & STATIC MOUNT ---
# Serve the Landing Page
@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

# Serve all other assets (css, js, images)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
