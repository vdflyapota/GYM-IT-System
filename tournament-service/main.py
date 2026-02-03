"""
Tournament Service - Microservice for Tournament Management
Part of GYM IT System - Software Architecture Course Project
Owner: Danial Rakhat
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from models import tournament_models
from routers import tournaments

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tournament Service",
    description="Microservice for Tournament Management - Brackets, Match Scheduling, Scoring Logic",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for communication with frontend and other services
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint for Kubernetes
@app.get("/health")
def health_check():
    """Health check endpoint for load balancers and Kubernetes"""
    return {"status": "healthy", "service": "tournament-service"}

# Register tournament routes
app.include_router(tournaments.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
