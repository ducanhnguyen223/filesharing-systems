from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth import schemas, service

router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer()

def get_current_user_dep(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    return service.get_current_user(credentials.credentials, db)

@router.post("/register", response_model=schemas.TokenResponse)
def register(data: schemas.RegisterRequest, db: Session = Depends(get_db)):
    token = service.register_user(data, db)
    return {"access_token": token}

@router.post("/login", response_model=schemas.TokenResponse)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    token = service.login_user(data, db)
    return {"access_token": token}

@router.get("/me", response_model=schemas.UserResponse)
def me(user=Depends(get_current_user_dep)):
    return {**user.__dict__, "plan_name": user.plan.name}
