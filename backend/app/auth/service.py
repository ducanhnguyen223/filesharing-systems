from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.core.models import User, Plan
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.auth.schemas import RegisterRequest, LoginRequest
import jwt

def register_user(data: RegisterRequest, db: Session) -> str:
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    free_plan = db.query(Plan).filter(Plan.name == "free").first()
    user = User(email=data.email, password_hash=hash_password(data.password), plan_id=free_plan.id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return create_access_token(user.id)

def login_user(data: LoginRequest, db: Session) -> str:
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return create_access_token(user.id)

def get_current_user(token: str, db: Session) -> User:
    try:
        user_id = decode_access_token(token)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
