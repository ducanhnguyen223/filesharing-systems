from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.files.storage import StorageClient, get_storage_client
from app.auth import schemas, service

router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer()

def get_current_user_dep(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    return service.get_current_user(credentials.credentials, db)

def get_storage_dep() -> StorageClient:
    return get_storage_client()

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

@router.patch("/me", response_model=schemas.UserResponse)
def update_me(
    data: schemas.UpdateProfileRequest,
    user=Depends(get_current_user_dep),
    db: Session = Depends(get_db),
):
    updated = service.update_profile(user, data, db)
    return {**updated.__dict__, "plan_name": updated.plan.name}

@router.delete("/me", status_code=204)
def delete_me(
    user=Depends(get_current_user_dep),
    db: Session = Depends(get_db),
    storage: StorageClient = Depends(get_storage_dep),
):
    service.delete_account(user, db, storage)
