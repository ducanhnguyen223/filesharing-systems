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
