# FileSharing System — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Xây dựng mini Google Drive hoàn chỉnh với auth, upload/download, share link, free/pro tier, deploy trên DigitalOcean.

**Architecture:** FastAPI monolith với 4 modules (auth, files, shares, billing), Vue.js SPA frontend, PostgreSQL cho metadata, DO Spaces cho file storage. Deploy trên DO App Platform với CI/CD qua GitHub Actions.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy 2.0 (sync) + psycopg2, Alembic, PyJWT, passlib[bcrypt], boto3, Vue.js 3 + Vite + Pinia, pytest + httpx, Docker, GitHub Actions

---

## Task 1: Project Bootstrap

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/Dockerfile`
- Create: `backend/app/__init__.py`
- Create: `docker-compose.yml`
- Create: `.gitignore`

**Step 1: Tạo cấu trúc thư mục**

```bash
mkdir -p backend/app/{auth,files,shares,billing,core}
mkdir -p backend/tests
mkdir -p backend/alembic
touch backend/app/__init__.py
touch backend/app/auth/__init__.py
touch backend/app/files/__init__.py
touch backend/app/shares/__init__.py
touch backend/app/billing/__init__.py
touch backend/app/core/__init__.py
touch backend/tests/__init__.py
```

**Step 2: Tạo `backend/requirements.txt`**

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.36
psycopg2-binary==2.9.9
alembic==1.13.3
pydantic-settings==2.5.2
pyjwt==2.9.0
passlib[bcrypt]==1.7.4
boto3==1.35.0
python-multipart==0.0.12
pytest==8.3.3
httpx==0.27.2
pytest-cov==5.0.0
moto[s3]==5.0.17
```

**Step 3: Tạo `backend/Dockerfile`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Step 4: Tạo `docker-compose.yml` (local dev)**

```yaml
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: filesharing
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/filesharing
      - SECRET_KEY=dev-secret-key-change-in-prod
      - SPACES_KEY=minioadmin
      - SPACES_SECRET=minioadmin
      - SPACES_BUCKET=filesharing
      - SPACES_REGION=us-east-1
      - SPACES_ENDPOINT=http://minio:9000
    depends_on:
      - db
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data

volumes:
  postgres_data:
  minio_data:
```

> MinIO là S3-compatible, dùng để dev local thay DO Spaces.

**Step 5: Tạo `.gitignore`**

```
__pycache__/
*.pyc
.env
.env.*
!.env.example
venv/
.venv/
node_modules/
dist/
*.egg-info/
.pytest_cache/
.coverage
```

**Step 6: Commit**

```bash
git init
git add .
git commit -m "chore: project bootstrap with docker-compose and requirements"
```

---

## Task 2: Core Config & Database

**Files:**
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/database.py`
- Create: `backend/tests/test_core.py`

**Step 1: Viết failing test cho config**

```python
# backend/tests/test_core.py
import os
import pytest
from app.core.config import Settings

def test_settings_loads_from_env():
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
    os.environ["SECRET_KEY"] = "test-secret"
    os.environ["SPACES_KEY"] = "key"
    os.environ["SPACES_SECRET"] = "secret"
    os.environ["SPACES_BUCKET"] = "bucket"
    os.environ["SPACES_REGION"] = "nyc3"
    os.environ["SPACES_ENDPOINT"] = "https://nyc3.digitaloceanspaces.com"

    settings = Settings()
    assert settings.DATABASE_URL == "postgresql://test:test@localhost/test"
    assert settings.SECRET_KEY == "test-secret"
```

**Step 2: Chạy test để verify fail**

```bash
cd backend && pytest tests/test_core.py -v
```
Expected: `ImportError: cannot import name 'Settings'`

**Step 3: Tạo `backend/app/core/config.py`**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    SPACES_KEY: str
    SPACES_SECRET: str
    SPACES_BUCKET: str
    SPACES_REGION: str
    SPACES_ENDPOINT: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    class Config:
        env_file = ".env"

settings = Settings()
```

**Step 4: Tạo `backend/app/core/database.py`**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Step 5: Chạy test**

```bash
cd backend && pytest tests/test_core.py -v
```
Expected: PASS

**Step 6: Commit**

```bash
git add backend/app/core/ backend/tests/test_core.py
git commit -m "feat: core config and database setup"
```

---

## Task 3: Models & Alembic Migration

**Files:**
- Create: `backend/app/core/models.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`

**Step 1: Tạo `backend/app/core/models.py`**

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, BigInteger, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.database import Base

class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)          # "free" / "pro"
    storage_limit = Column(BigInteger, nullable=False)          # bytes
    file_size_limit = Column(BigInteger, nullable=False)        # bytes per file
    price_monthly = Column(Float, default=0.0)
    users = relationship("User", back_populates="plan")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    storage_used = Column(BigInteger, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    plan_id = Column(Integer, ForeignKey("plans.id"))
    plan = relationship("Plan", back_populates="users")
    files = relationship("File", back_populates="owner")

class File(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    size = Column(BigInteger, nullable=False)
    mimetype = Column(String)
    spaces_key = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    owner = relationship("User", back_populates="files")
    shares = relationship("Share", back_populates="file")

class Share(Base):
    __tablename__ = "shares"
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    file = relationship("File", back_populates="shares")
```

**Step 2: Setup Alembic**

```bash
cd backend && alembic init alembic
```

**Step 3: Sửa `backend/alembic/env.py`** — thay phần `target_metadata`:

```python
# Thêm vào đầu file sau import config
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import Base
from app.core.models import Plan, User, File, Share  # noqa: import models
from app.core.config import settings

# Thay dòng: target_metadata = None
target_metadata = Base.metadata

# Thay dòng config.set_main_option("sqlalchemy.url", ...)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

**Step 4: Tạo migration đầu tiên**

```bash
cd backend && alembic revision --autogenerate -m "initial tables"
```
Expected: tạo file trong `alembic/versions/`

**Step 5: Tạo `backend/tests/conftest.py`** (shared fixtures cho tất cả tests)

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.core.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    # Seed plans
    from app.core.models import Plan
    free = Plan(name="free", storage_limit=5*1024**3, file_size_limit=100*1024**2, price_monthly=0)
    pro = Plan(name="pro", storage_limit=50*1024**3, file_size_limit=1024**3, price_monthly=9.99)
    db.add_all([free, pro])
    db.commit()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

**Step 6: Commit**

```bash
git add backend/app/core/models.py backend/alembic/ backend/tests/conftest.py
git commit -m "feat: database models and alembic migration setup"
```

---

## Task 4: Auth Module

**Files:**
- Create: `backend/app/core/security.py`
- Create: `backend/app/auth/schemas.py`
- Create: `backend/app/auth/service.py`
- Create: `backend/app/auth/router.py`
- Create: `backend/app/main.py`
- Create: `backend/tests/test_auth.py`

**Step 1: Tạo `backend/app/core/security.py`**

```python
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": expire}, settings.SECRET_KEY, algorithm="HS256")

def decode_access_token(token: str) -> int:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    return int(payload["sub"])
```

**Step 2: Tạo `backend/app/auth/schemas.py`**

```python
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

    class Config:
        from_attributes = True
```

**Step 3: Tạo `backend/app/auth/service.py`**

```python
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
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
```

**Step 4: Tạo `backend/app/auth/router.py`**

```python
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
```

**Step 5: Tạo `backend/app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.router import router as auth_router

app = FastAPI(title="FileSharing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

@app.get("/health")
def health():
    return {"status": "ok"}
```

**Step 6: Viết `backend/tests/test_auth.py`**

```python
def test_register_success(client):
    res = client.post("/auth/register", json={"email": "test@example.com", "password": "password123"})
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_register_duplicate_email(client):
    client.post("/auth/register", json={"email": "test@example.com", "password": "pass"})
    res = client.post("/auth/register", json={"email": "test@example.com", "password": "pass"})
    assert res.status_code == 400

def test_login_success(client):
    client.post("/auth/register", json={"email": "test@example.com", "password": "password123"})
    res = client.post("/auth/login", json={"email": "test@example.com", "password": "password123"})
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "test@example.com", "password": "password123"})
    res = client.post("/auth/login", json={"email": "test@example.com", "password": "wrong"})
    assert res.status_code == 401

def test_me_requires_auth(client):
    res = client.get("/auth/me")
    assert res.status_code == 403

def test_me_returns_user(client):
    res = client.post("/auth/register", json={"email": "test@example.com", "password": "pass"})
    token = res.json()["access_token"]
    res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "test@example.com"
    assert res.json()["plan_name"] == "free"
```

**Step 7: Chạy tests**

```bash
cd backend && SECRET_KEY=test SPACES_KEY=k SPACES_SECRET=s SPACES_BUCKET=b SPACES_REGION=r SPACES_ENDPOINT=e pytest tests/test_auth.py -v
```
Expected: 6 PASSED

**Step 8: Commit**

```bash
git add backend/app/ backend/tests/test_auth.py
git commit -m "feat: auth module with register, login, JWT"
```

---

## Task 5: DO Spaces Storage Client

**Files:**
- Create: `backend/app/core/storage.py`
- Create: `backend/tests/test_storage.py`

**Step 1: Viết failing test**

```python
# backend/tests/test_storage.py
import pytest
import boto3
from moto import mock_aws
from app.core.storage import StorageClient

@mock_aws
def test_upload_and_get_download_url():
    # Setup fake S3
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="test-bucket")

    client = StorageClient(
        key="fake", secret="fake",
        bucket="test-bucket", region="us-east-1",
        endpoint=None
    )
    client.upload(b"hello world", "test/file.txt", "text/plain")
    url = client.get_download_url("test/file.txt", filename="file.txt")
    assert "test/file.txt" in url

@mock_aws
def test_delete_file():
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="test-bucket")

    client = StorageClient(key="fake", secret="fake", bucket="test-bucket", region="us-east-1", endpoint=None)
    client.upload(b"data", "test/del.txt", "text/plain")
    client.delete("test/del.txt")
    # Should not raise
```

**Step 2: Chạy test để verify fail**

```bash
cd backend && SECRET_KEY=test SPACES_KEY=k SPACES_SECRET=s SPACES_BUCKET=b SPACES_REGION=r SPACES_ENDPOINT=e pytest tests/test_storage.py -v
```
Expected: `ImportError`

**Step 3: Tạo `backend/app/core/storage.py`**

```python
import boto3
from botocore.client import Config

class StorageClient:
    def __init__(self, key: str, secret: str, bucket: str, region: str, endpoint: str | None):
        kwargs = dict(
            aws_access_key_id=key,
            aws_secret_access_key=secret,
            region_name=region,
            config=Config(signature_version="s3v4"),
        )
        if endpoint:
            kwargs["endpoint_url"] = endpoint
        self.s3 = boto3.client("s3", **kwargs)
        self.bucket = bucket

    def upload(self, data: bytes, key: str, content_type: str):
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=data, ContentType=content_type)

    def get_download_url(self, key: str, filename: str, expires: int = 3600) -> str:
        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key,
                    "ResponseContentDisposition": f'attachment; filename="{filename}"'},
            ExpiresIn=expires,
        )

    def delete(self, key: str):
        self.s3.delete_object(Bucket=self.bucket, Key=key)


def get_storage() -> StorageClient:
    from app.core.config import settings
    return StorageClient(
        key=settings.SPACES_KEY,
        secret=settings.SPACES_SECRET,
        bucket=settings.SPACES_BUCKET,
        region=settings.SPACES_REGION,
        endpoint=settings.SPACES_ENDPOINT,
    )
```

**Step 4: Chạy tests**

```bash
cd backend && SECRET_KEY=test SPACES_KEY=k SPACES_SECRET=s SPACES_BUCKET=b SPACES_REGION=r SPACES_ENDPOINT=e pytest tests/test_storage.py -v
```
Expected: 2 PASSED

**Step 5: Commit**

```bash
git add backend/app/core/storage.py backend/tests/test_storage.py
git commit -m "feat: DO Spaces storage client with moto tests"
```

---

## Task 6: Files Module

**Files:**
- Create: `backend/app/files/schemas.py`
- Create: `backend/app/files/service.py`
- Create: `backend/app/files/router.py`
- Create: `backend/tests/test_files.py`
- Modify: `backend/app/main.py`

**Step 1: Tạo `backend/app/files/schemas.py`**

```python
from pydantic import BaseModel
from datetime import datetime

class FileResponse(BaseModel):
    id: int
    filename: str
    size: int
    mimetype: str | None
    created_at: datetime

    class Config:
        from_attributes = True

class UploadResponse(BaseModel):
    file: FileResponse
    message: str = "Upload successful"
```

**Step 2: Tạo `backend/app/files/service.py`**

```python
import uuid
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.core.models import User, File
from app.core.storage import StorageClient

def check_quota(user: User, file_size: int):
    plan = user.plan
    if file_size > plan.file_size_limit:
        raise HTTPException(400, f"File exceeds {plan.file_size_limit // 1024**2}MB limit for your plan")
    if user.storage_used + file_size > plan.storage_limit:
        raise HTTPException(400, "Storage quota exceeded. Upgrade to Pro.")

def upload_file(upload: UploadFile, user: User, db: Session, storage: StorageClient) -> File:
    data = upload.file.read()
    check_quota(user, len(data))
    key = f"{user.id}/{uuid.uuid4()}/{upload.filename}"
    storage.upload(data, key, upload.content_type or "application/octet-stream")
    file = File(user_id=user.id, filename=upload.filename, size=len(data),
                mimetype=upload.content_type, spaces_key=key)
    db.add(file)
    user.storage_used += len(data)
    db.commit()
    db.refresh(file)
    return file

def list_files(user: User, db: Session) -> list[File]:
    return db.query(File).filter(File.user_id == user.id, File.is_deleted == False).all()

def get_download_url(file_id: int, user: User, db: Session, storage: StorageClient) -> str:
    file = db.query(File).filter(File.id == file_id, File.user_id == user.id, File.is_deleted == False).first()
    if not file:
        raise HTTPException(404, "File not found")
    return storage.get_download_url(file.spaces_key, file.filename)

def delete_file(file_id: int, user: User, db: Session, storage: StorageClient):
    file = db.query(File).filter(File.id == file_id, File.user_id == user.id, File.is_deleted == False).first()
    if not file:
        raise HTTPException(404, "File not found")
    storage.delete(file.spaces_key)
    file.is_deleted = True
    user.storage_used -= file.size
    db.commit()
```

**Step 3: Tạo `backend/app/files/router.py`**

```python
from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.storage import get_storage, StorageClient
from app.auth.router import get_current_user_dep
from app.files import schemas, service

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/upload", response_model=schemas.UploadResponse)
def upload(file: UploadFile = FastAPIFile(...), user=Depends(get_current_user_dep),
           db: Session = Depends(get_db), storage: StorageClient = Depends(get_storage)):
    f = service.upload_file(file, user, db, storage)
    return {"file": f}

@router.get("/", response_model=list[schemas.FileResponse])
def list_files(user=Depends(get_current_user_dep), db: Session = Depends(get_db)):
    return service.list_files(user, db)

@router.get("/{file_id}/download")
def download(file_id: int, user=Depends(get_current_user_dep),
             db: Session = Depends(get_db), storage: StorageClient = Depends(get_storage)):
    url = service.get_download_url(file_id, user, db, storage)
    return {"download_url": url}

@router.delete("/{file_id}", status_code=204)
def delete(file_id: int, user=Depends(get_current_user_dep),
           db: Session = Depends(get_db), storage: StorageClient = Depends(get_storage)):
    service.delete_file(file_id, user, db, storage)
```

**Step 4: Update `backend/app/main.py`**

```python
# Thêm vào phần imports và include_router
from app.files.router import router as files_router
app.include_router(files_router)
```

**Step 5: Viết `backend/tests/test_files.py`**

```python
import io
from moto import mock_aws
import boto3

def make_bucket(bucket="test-bucket"):
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket=bucket)

def get_auth_header(client):
    client.post("/auth/register", json={"email": "u@test.com", "password": "pass"})
    res = client.post("/auth/login", json={"email": "u@test.com", "password": "pass"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}

@mock_aws
def test_upload_and_list(client, monkeypatch):
    make_bucket()
    monkeypatch.setenv("SPACES_BUCKET", "test-bucket")
    monkeypatch.setenv("SPACES_REGION", "us-east-1")
    monkeypatch.setenv("SPACES_ENDPOINT", "")
    headers = get_auth_header(client)
    res = client.post("/files/upload", headers=headers,
                      files={"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")})
    assert res.status_code == 200
    assert res.json()["file"]["filename"] == "test.txt"

    res = client.get("/files/", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 1

@mock_aws
def test_delete_file(client, monkeypatch):
    make_bucket()
    monkeypatch.setenv("SPACES_BUCKET", "test-bucket")
    monkeypatch.setenv("SPACES_REGION", "us-east-1")
    monkeypatch.setenv("SPACES_ENDPOINT", "")
    headers = get_auth_header(client)
    res = client.post("/files/upload", headers=headers,
                      files={"file": ("del.txt", io.BytesIO(b"data"), "text/plain")})
    file_id = res.json()["file"]["id"]
    res = client.delete(f"/files/{file_id}", headers=headers)
    assert res.status_code == 204
    res = client.get("/files/", headers=headers)
    assert len(res.json()) == 0
```

**Step 6: Chạy tests**

```bash
cd backend && SECRET_KEY=test SPACES_KEY=k SPACES_SECRET=s SPACES_BUCKET=b SPACES_REGION=r SPACES_ENDPOINT=e pytest tests/test_files.py -v
```
Expected: 2 PASSED

**Step 7: Commit**

```bash
git add backend/app/files/ backend/tests/test_files.py backend/app/main.py
git commit -m "feat: files module with upload, download, list, delete"
```

---

## Task 7: Shares Module

**Files:**
- Create: `backend/app/shares/schemas.py`
- Create: `backend/app/shares/service.py`
- Create: `backend/app/shares/router.py`
- Create: `backend/tests/test_shares.py`
- Modify: `backend/app/main.py`

**Step 1: Tạo `backend/app/shares/schemas.py`**

```python
from pydantic import BaseModel
from datetime import datetime

class ShareResponse(BaseModel):
    id: int
    token: str
    created_at: datetime
    share_url: str

class PublicFileInfo(BaseModel):
    filename: str
    size: int
    download_url: str
```

**Step 2: Tạo `backend/app/shares/service.py`**

```python
import secrets
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.models import File, Share
from app.core.storage import StorageClient

def create_share(file_id: int, user_id: int, db: Session) -> Share:
    file = db.query(File).filter(File.id == file_id, File.user_id == user_id, File.is_deleted == False).first()
    if not file:
        raise HTTPException(404, "File not found")
    token = secrets.token_urlsafe(16)
    share = Share(file_id=file_id, token=token)
    db.add(share)
    db.commit()
    db.refresh(share)
    return share

def get_public_file(token: str, db: Session, storage: StorageClient) -> dict:
    share = db.query(Share).filter(Share.token == token).first()
    if not share or share.file.is_deleted:
        raise HTTPException(404, "Share link not found or expired")
    file = share.file
    url = storage.get_download_url(file.spaces_key, file.filename)
    return {"filename": file.filename, "size": file.size, "download_url": url}
```

**Step 3: Tạo `backend/app/shares/router.py`**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.storage import get_storage, StorageClient
from app.auth.router import get_current_user_dep
from app.shares import schemas, service

router = APIRouter(tags=["shares"])

@router.post("/files/{file_id}/share", response_model=schemas.ShareResponse)
def create_share(file_id: int, request=None, user=Depends(get_current_user_dep),
                 db: Session = Depends(get_db)):
    share = service.create_share(file_id, user.id, db)
    return {**share.__dict__, "share_url": f"/share/{share.token}"}

@router.get("/share/{token}", response_model=schemas.PublicFileInfo)
def public_share(token: str, db: Session = Depends(get_db),
                 storage: StorageClient = Depends(get_storage)):
    return service.get_public_file(token, db, storage)
```

**Step 4: Update `backend/app/main.py`**

```python
from app.shares.router import router as shares_router
app.include_router(shares_router)
```

**Step 5: Viết `backend/tests/test_shares.py`**

```python
import io
from moto import mock_aws
import boto3

def setup_user_with_file(client, monkeypatch):
    monkeypatch.setenv("SPACES_BUCKET", "test-bucket")
    monkeypatch.setenv("SPACES_REGION", "us-east-1")
    monkeypatch.setenv("SPACES_ENDPOINT", "")
    client.post("/auth/register", json={"email": "u@test.com", "password": "pass"})
    res = client.post("/auth/login", json={"email": "u@test.com", "password": "pass"})
    headers = {"Authorization": f"Bearer {res.json()['access_token']}"}
    res = client.post("/files/upload", headers=headers,
                      files={"file": ("doc.txt", io.BytesIO(b"content"), "text/plain")})
    return headers, res.json()["file"]["id"]

@mock_aws
def test_create_and_access_share(client, monkeypatch):
    boto3.client("s3", region_name="us-east-1").create_bucket(Bucket="test-bucket")
    headers, file_id = setup_user_with_file(client, monkeypatch)
    res = client.post(f"/files/{file_id}/share", headers=headers)
    assert res.status_code == 200
    token = res.json()["token"]

    res = client.get(f"/share/{token}")
    assert res.status_code == 200
    assert res.json()["filename"] == "doc.txt"
    assert "download_url" in res.json()

@mock_aws
def test_invalid_share_token(client, monkeypatch):
    monkeypatch.setenv("SPACES_BUCKET", "test-bucket")
    monkeypatch.setenv("SPACES_REGION", "us-east-1")
    monkeypatch.setenv("SPACES_ENDPOINT", "")
    boto3.client("s3", region_name="us-east-1").create_bucket(Bucket="test-bucket")
    res = client.get("/share/invalid-token-xyz")
    assert res.status_code == 404
```

**Step 6: Chạy tests**

```bash
cd backend && SECRET_KEY=test SPACES_KEY=k SPACES_SECRET=s SPACES_BUCKET=b SPACES_REGION=r SPACES_ENDPOINT=e pytest tests/ -v
```
Expected: tất cả tests PASSED

**Step 7: Commit**

```bash
git add backend/app/shares/ backend/tests/test_shares.py backend/app/main.py
git commit -m "feat: shares module with public share links"
```

---

## Task 8: Frontend Setup

**Files:**
- Create: `frontend/` (Vue 3 + Vite project)
- Create: `frontend/Dockerfile`
- Create: `frontend/src/api/index.js`

**Step 1: Khởi tạo Vue project**

```bash
cd filesharing_systems
npm create vue@latest frontend
# Chọn: Yes TypeScript? No | Add Vue Router? Yes | Add Pinia? Yes | Add ESLint? Yes
cd frontend && npm install
npm install axios
```

**Step 2: Tạo `frontend/src/api/index.js`**

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const authApi = {
  register: (email, password) => api.post('/auth/register', { email, password }),
  login: (email, password) => api.post('/auth/login', { email, password }),
  me: () => api.get('/auth/me'),
}

export const filesApi = {
  list: () => api.get('/files/'),
  upload: (formData) => api.post('/files/upload', formData),
  download: (id) => api.get(`/files/${id}/download`),
  delete: (id) => api.delete(`/files/${id}`),
  share: (id) => api.post(`/files/${id}/share`),
}

export const shareApi = {
  getPublic: (token) => api.get(`/share/${token}`),
}
```

**Step 3: Tạo `frontend/src/stores/auth.js`**

```javascript
import { defineStore } from 'pinia'
import { authApi } from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({ user: null, token: localStorage.getItem('token') }),
  getters: { isLoggedIn: (s) => !!s.token },
  actions: {
    async login(email, password) {
      const res = await authApi.login(email, password)
      this.token = res.data.access_token
      localStorage.setItem('token', this.token)
      await this.fetchUser()
    },
    async register(email, password) {
      const res = await authApi.register(email, password)
      this.token = res.data.access_token
      localStorage.setItem('token', this.token)
      await this.fetchUser()
    },
    async fetchUser() {
      const res = await authApi.me()
      this.user = res.data
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('token')
    },
  },
})
```

**Step 4: Setup router `frontend/src/router/index.js`**

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login', component: () => import('@/views/LoginView.vue') },
  { path: '/register', component: () => import('@/views/RegisterView.vue') },
  { path: '/', component: () => import('@/views/DashboardView.vue'), meta: { requiresAuth: true } },
  { path: '/share/:token', component: () => import('@/views/ShareView.vue') },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) return '/login'
})

export default router
```

**Step 5: Tạo `frontend/Dockerfile`**

```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

**Step 6: Tạo `frontend/nginx.conf`**

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;
    location / { try_files $uri $uri/ /index.html; }
}
```

**Step 7: Commit**

```bash
git add frontend/
git commit -m "feat: frontend scaffold with Vue 3, Pinia, router, API client"
```

---

## Task 9: Frontend Views

**Files:**
- Create: `frontend/src/views/LoginView.vue`
- Create: `frontend/src/views/RegisterView.vue`
- Create: `frontend/src/views/DashboardView.vue`
- Create: `frontend/src/views/ShareView.vue`

**Step 1: `frontend/src/views/LoginView.vue`**

```vue
<template>
  <div class="auth-container">
    <h1>Login</h1>
    <form @submit.prevent="submit">
      <input v-model="email" type="email" placeholder="Email" required />
      <input v-model="password" type="password" placeholder="Password" required />
      <button type="submit">Login</button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
    <p>No account? <RouterLink to="/register">Register</RouterLink></p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const email = ref(''), password = ref(''), error = ref('')
const auth = useAuthStore(), router = useRouter()

async function submit() {
  try {
    await auth.login(email.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Login failed'
  }
}
</script>
```

**Step 2: `frontend/src/views/RegisterView.vue`**

```vue
<template>
  <div class="auth-container">
    <h1>Register</h1>
    <form @submit.prevent="submit">
      <input v-model="email" type="email" placeholder="Email" required />
      <input v-model="password" type="password" placeholder="Password" required />
      <button type="submit">Create Account</button>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
    <p>Have an account? <RouterLink to="/login">Login</RouterLink></p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const email = ref(''), password = ref(''), error = ref('')
const auth = useAuthStore(), router = useRouter()

async function submit() {
  try {
    await auth.register(email.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Registration failed'
  }
}
</script>
```

**Step 3: `frontend/src/views/DashboardView.vue`**

```vue
<template>
  <div class="dashboard">
    <header>
      <h1>My Files</h1>
      <div class="user-info" v-if="auth.user">
        {{ auth.user.email }} ({{ auth.user.plan_name }})
        — {{ formatBytes(auth.user.storage_used) }} used
        <button @click="auth.logout(); $router.push('/login')">Logout</button>
      </div>
    </header>

    <!-- Upload -->
    <div class="upload-section">
      <input type="file" ref="fileInput" @change="upload" />
      <p v-if="uploadError" class="error">{{ uploadError }}</p>
    </div>

    <!-- File list -->
    <table v-if="files.length">
      <tr v-for="f in files" :key="f.id">
        <td>{{ f.filename }}</td>
        <td>{{ formatBytes(f.size) }}</td>
        <td>
          <button @click="download(f.id)">Download</button>
          <button @click="share(f.id)">Share</button>
          <button @click="deleteFile(f.id)">Delete</button>
        </td>
      </tr>
    </table>
    <p v-else>No files yet. Upload one!</p>

    <div v-if="shareLink" class="share-link">
      Share link: <a :href="shareLink" target="_blank">{{ shareLink }}</a>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { filesApi } from '@/api'

const auth = useAuthStore()
const files = ref([]), fileInput = ref(null), uploadError = ref(''), shareLink = ref('')

onMounted(async () => {
  await auth.fetchUser()
  const res = await filesApi.list()
  files.value = res.data
})

async function upload(e) {
  const file = e.target.files[0]
  if (!file) return
  const fd = new FormData()
  fd.append('file', file)
  try {
    await filesApi.upload(fd)
    const res = await filesApi.list()
    files.value = res.data
    await auth.fetchUser()
  } catch (err) {
    uploadError.value = err.response?.data?.detail || 'Upload failed'
  }
}

async function download(id) {
  const res = await filesApi.download(id)
  window.open(res.data.download_url, '_blank')
}

async function share(id) {
  const res = await filesApi.share(id)
  shareLink.value = `${window.location.origin}/share/${res.data.token}`
}

async function deleteFile(id) {
  await filesApi.delete(id)
  files.value = files.value.filter(f => f.id !== id)
  await auth.fetchUser()
}

function formatBytes(b) {
  if (b < 1024) return b + ' B'
  if (b < 1024**2) return (b/1024).toFixed(1) + ' KB'
  if (b < 1024**3) return (b/1024**2).toFixed(1) + ' MB'
  return (b/1024**3).toFixed(2) + ' GB'
}
</script>
```

**Step 4: `frontend/src/views/ShareView.vue`**

```vue
<template>
  <div class="share-page">
    <h1>Shared File</h1>
    <div v-if="file">
      <p>{{ file.filename }} ({{ formatBytes(file.size) }})</p>
      <a :href="file.download_url">Download</a>
    </div>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-else>Loading...</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { shareApi } from '@/api'

const route = useRoute()
const file = ref(null), error = ref('')

onMounted(async () => {
  try {
    const res = await shareApi.getPublic(route.params.token)
    file.value = res.data
  } catch {
    error.value = 'File not found or link expired.'
  }
})

function formatBytes(b) {
  if (b < 1024**2) return (b/1024).toFixed(1) + ' KB'
  if (b < 1024**3) return (b/1024**2).toFixed(1) + ' MB'
  return (b/1024**3).toFixed(2) + ' GB'
}
</script>
```

**Step 5: Kiểm tra frontend chạy được**

```bash
cd frontend && npm run dev
```
Expected: App chạy tại http://localhost:5173, không có lỗi compile.

**Step 6: Commit**

```bash
git add frontend/src/views/
git commit -m "feat: frontend views - login, register, dashboard, share page"
```

---

## Task 10: CI/CD GitHub Actions

**Files:**
- Create: `.github/workflows/deploy.yml`
- Create: `backend/.env.example`

**Step 1: Tạo `backend/.env.example`**

```
DATABASE_URL=postgresql://user:password@host:5432/dbname
SECRET_KEY=your-secret-key-here
SPACES_KEY=your-do-spaces-key
SPACES_SECRET=your-do-spaces-secret
SPACES_BUCKET=your-bucket-name
SPACES_REGION=nyc3
SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com
```

**Step 2: Tạo `.github/workflows/deploy.yml`**

```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: registry.digitalocean.com/your-registry
  BACKEND_IMAGE: registry.digitalocean.com/your-registry/backend
  FRONTEND_IMAGE: registry.digitalocean.com/your-registry/frontend

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r backend/requirements.txt
      - run: |
          cd backend
          SECRET_KEY=test \
          SPACES_KEY=k SPACES_SECRET=s \
          SPACES_BUCKET=b SPACES_REGION=us-east-1 \
          SPACES_ENDPOINT="" \
          DATABASE_URL=sqlite:///./test.db \
          pytest tests/ -v --cov=app

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

      - name: Login to DO Container Registry
        run: doctl registry login --expiry-seconds 1200

      - name: Build & push backend
        run: |
          docker build -t $BACKEND_IMAGE:${{ github.sha }} ./backend
          docker push $BACKEND_IMAGE:${{ github.sha }}
          docker tag $BACKEND_IMAGE:${{ github.sha }} $BACKEND_IMAGE:latest
          docker push $BACKEND_IMAGE:latest

      - name: Build & push frontend
        run: |
          docker build -t $FRONTEND_IMAGE:${{ github.sha }} ./frontend
          docker push $FRONTEND_IMAGE:${{ github.sha }}
          docker tag $FRONTEND_IMAGE:${{ github.sha }} $FRONTEND_IMAGE:latest
          docker push $FRONTEND_IMAGE:latest

      - name: Deploy to App Platform
        run: |
          doctl apps update ${{ secrets.DO_APP_ID }} --spec .do/app.yaml
```

**Step 3: Tạo `.do/app.yaml` (App Platform spec)**

```yaml
name: filesharing
region: sgp1

services:
  - name: backend
    image:
      registry_type: DOCR
      repository: backend
      tag: latest
    http_port: 8000
    envs:
      - key: DATABASE_URL
        scope: RUN_TIME
        value: ${db.DATABASE_URL}
      - key: SECRET_KEY
        scope: RUN_TIME
        value: ${SECRET_KEY}
      - key: SPACES_KEY
        scope: RUN_TIME
        value: ${SPACES_KEY}
      - key: SPACES_SECRET
        scope: RUN_TIME
        value: ${SPACES_SECRET}
      - key: SPACES_BUCKET
        scope: RUN_TIME
        value: ${SPACES_BUCKET}
      - key: SPACES_REGION
        scope: RUN_TIME
        value: ${SPACES_REGION}
      - key: SPACES_ENDPOINT
        scope: RUN_TIME
        value: ${SPACES_ENDPOINT}
    run_command: uvicorn app.main:app --host 0.0.0.0 --port 8000

  - name: frontend
    image:
      registry_type: DOCR
      repository: frontend
      tag: latest
    http_port: 80

databases:
  - name: db
    engine: PG
    version: "15"
    size: db-s-1vcpu-1gb
```

**Step 4: Commit**

```bash
mkdir -p .do
git add .github/ .do/ backend/.env.example
git commit -m "ci: GitHub Actions CI/CD pipeline with DO Container Registry and App Platform"
```

---

## Task 11: Alembic Migration & Seed Plans (Production)

**Step 1: Tạo `backend/seed_plans.py`** (chạy 1 lần trên production)

```python
"""Seed initial plans. Run with: python seed_plans.py"""
from app.core.database import SessionLocal
from app.core.models import Plan

db = SessionLocal()
if not db.query(Plan).first():
    db.add_all([
        Plan(name="free", storage_limit=5*1024**3, file_size_limit=100*1024**2, price_monthly=0),
        Plan(name="pro", storage_limit=50*1024**3, file_size_limit=1024**3, price_monthly=9.99),
    ])
    db.commit()
    print("Plans seeded.")
else:
    print("Plans already exist.")
db.close()
```

**Step 2: Update `backend/Dockerfile`** — chạy migration tự động khi deploy

```dockerfile
# Thay CMD thành:
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Step 3: Commit**

```bash
git add backend/seed_plans.py backend/Dockerfile
git commit -m "feat: auto-run alembic migrations on startup, add plan seeder"
```

---

## Task 12: README & Final Check

**Step 1: Tạo `README.md`**

```markdown
# FileSharing System

Mini Google Drive — upload, share, manage files.

## Local Development

```bash
docker-compose up --build
```

- Backend API: http://localhost:8000/docs
- Frontend: http://localhost:5173 (run separately: `cd frontend && npm run dev`)
- MinIO console: http://localhost:9001 (user: minioadmin / minioadmin)

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in values.

## Deploy to DigitalOcean

1. Create DO Container Registry
2. Create DO Spaces bucket
3. Add GitHub Secrets: `DIGITALOCEAN_ACCESS_TOKEN`, `DO_APP_ID`, `SECRET_KEY`, `SPACES_*`
4. Push to `main` branch → CI/CD triggers automatically

## Run Migrations

```bash
cd backend && alembic upgrade head
```
```

**Step 2: Chạy toàn bộ test suite lần cuối**

```bash
cd backend && SECRET_KEY=test SPACES_KEY=k SPACES_SECRET=s SPACES_BUCKET=b SPACES_REGION=us-east-1 SPACES_ENDPOINT="" DATABASE_URL=sqlite:///./test.db pytest tests/ -v
```
Expected: tất cả PASSED

**Step 3: Final commit**

```bash
git add README.md
git commit -m "docs: add README with local dev and deploy instructions"
```

---

## Summary

| Task | Nội dung |
|---|---|
| 1 | Project bootstrap (Docker, requirements) |
| 2 | Core config & database |
| 3 | Models + Alembic migrations |
| 4 | Auth module (register, login, JWT) |
| 5 | DO Spaces storage client |
| 6 | Files module (upload, download, list, delete) |
| 7 | Shares module (public share links) |
| 8 | Frontend setup (Vue 3 + Pinia + Router) |
| 9 | Frontend views (Login, Dashboard, Share page) |
| 10 | CI/CD (GitHub Actions + DO App Platform) |
| 11 | Alembic auto-migration + plan seeder |
| 12 | README + final verification |
