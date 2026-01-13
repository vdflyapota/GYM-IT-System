# routers/auth.py
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from models.user_models import User

# --- SECURITY CONFIGURATION ---
# Store these in environment variables! .env
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(prefix="/auth", tags=["User Management & Security"])

# Password Hashing Tool
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# This tells FastAPI that the client must send "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- SCHEMAS ---
class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    # FIX: "role" is removed here to prevent Mass Assignment / Privilege Escalation

class RoleUpdate(BaseModel):
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str # Returning role helps frontend UI logic
    full_name: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    class Config:
        from_attributes = True

# --- HELPER FUNCTIONS ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- CRITICAL SECURITY DEPENDENCIES ---

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    FIX: This validates the digital signature of the JWT.
    If a hacker changes the token, the signature fails.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_admin(current_user: User = Depends(get_current_user)):
    """
    FIX: Broken Access Control.
    We rely on the TRUSTED database record, not user input.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access Denied: Admins Only"
        )
    return current_user

# --- ENDPOINTS ---

@router.post("/register", response_model=UserResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    # 1. Check existing
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Hash Password (Secure)
    hashed_pw = get_password_hash(user.password)
    
    # 3. Create User - FIX: FORCE ROLE TO "MEMBER"
    new_user = User(
        email=user.email,
        hashed_password=hashed_pw,
        full_name=user.full_name,
        role="member" # Hardcoded safety
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(item: UserRegister, db: Session = Depends(get_db)):
    # Note: Using UserRegister schema just to get email/pass fields easily
    user = db.query(User).filter(User.email == item.email).first()
    
    # Secure Comparison
    if not user or not verify_password(item.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate Real JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer", 
        "role": user.role,
        "full_name": user.full_name
    }

# --- ADMIN ROUTES ---

@router.get("/users", response_model=List[UserResponse])
def get_all_users(current_user: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return db.query(User).all()

@router.put("/users/{user_id}/role")
def change_user_role(
    user_id: int, 
    update: RoleUpdate, 
    current_user: User = Depends(get_current_admin), 
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.role = update.role
    db.commit()
    return {"status": "success", "new_role": user.role}
