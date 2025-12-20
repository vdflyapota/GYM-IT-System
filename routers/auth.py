from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user_models import User
from pydantic import BaseModel
from passlib.context import CryptContext

router = APIRouter(prefix="/auth", tags=["User Management"])

# Security Setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic Schema (Validation)
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "member"

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # 1. Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Hash password (Security Characteristic)
    hashed_pw = pwd_context.hash(user.password)
    
    # 3. Save to DB
    new_user = User(
        email=user.email,
        hashed_password=hashed_pw,
        full_name=user.full_name,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "user_id": new_user.id}
