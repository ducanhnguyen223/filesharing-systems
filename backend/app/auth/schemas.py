from pydantic import BaseModel, EmailStr
from datetime import datetime

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: str
    storage_used: int
    created_at: datetime
    plan_name: str

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    email: EmailStr | None = None
    current_password: str | None = None
    new_password: str | None = None
