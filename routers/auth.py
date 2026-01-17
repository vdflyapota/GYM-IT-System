from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models.user_models import User

# --- CONFIGURATION ---
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(prefix="/auth", tags=["User Management"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- SCHEMAS ---
class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str

class RoleUpdate(BaseModel):
    role: str

class StatusUpdate(BaseModel):
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    full_name: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    class Config:
        from_attributes = True

# --- HELPERS ---
def verify_password(plain, hashed): return pwd_context.verify(plain, hashed)
def get_password_hash(password): return pwd_context.hash(password)
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- DEPENDENCIES ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None: raise HTTPException(status_code=401)
    except JWTError:
        raise HTTPException(status_code=401)
    
    user = db.query(User).filter(User.email == email).first()
    if user is None: raise HTTPException(status_code=401)
    return user

# --- NEW: TRAINER GATEKEEPER ---
def get_current_trainer(current_user: User = Depends(get_current_user)):
    # ALLOW if role is 'trainer' OR 'admin'
    if current_user.role not in ["trainer", "admin"]:
        raise HTTPException(
            status_code=403, 
            detail="Access Denied: Only Trainers or Admins can perform this action."
        )
    return current_user

# --- ADMIN GATEKEEPER ---
def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admins Only")
    return current_user

# --- ENDPOINTS ---

@router.post("/register", response_model=UserResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Defaults: role="member", is_active=False (Must be approved by Admin)
    new_user = User(
        email=user.email,
        hashed_password=get_password_hash(user.password),
        full_name=user.full_name,
        role="member",
        is_active=False 
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(item: UserRegister, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == item.email).first()
    if not user or not verify_password(item.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account pending approval. Please contact the Admin.")

    access_token = create_access_token(data={"sub": user.email})
    
    # Set Secure Cookie for Admin Page Access
    response.set_cookie(
        key="access_token", value=f"Bearer {access_token}", httponly=True, samesite="lax"
    )
    
    return {"access_token": access_token, "token_type": "bearer", "role": user.role, "full_name": user.full_name}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# --- ADMIN ENDPOINTS ---

@router.get("/users", response_model=List[UserResponse])
def get_all_users(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(User).all()

@router.put("/users/{user_id}/role")
def change_user_role(user_id: int, update: RoleUpdate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404)
    user.role = update.role
    db.commit()
    return {"status": "success", "role": user.role}

@router.put("/users/{user_id}/status")
def change_user_status(user_id: int, update: StatusUpdate, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404)
    user.is_active = update.is_active
    db.commit()
    return {"status": "success", "is_active": user.is_active}



@router.delete("/users/{user_id}")
def delete_user(user_id: int, admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    # 1. Prevent Admin from deleting themselves
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account.")

    # 2. Find User
    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="User not found")

    # 3. Delete
    db.delete(user_to_delete)
    db.commit()
    return {"status": "success", "message": f"User {user_to_delete.email} deleted permanently."}
