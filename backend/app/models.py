"""SQLAlchemy ORM models for all SBI Saathi database tables."""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    mobile = Column(String(15), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    is_verified = Column(Boolean, default=False)
    is_profile_complete = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False)
    applications = relationship("Application", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(10), nullable=False)  # Male, Female, Other
    state = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    occupation = Column(String(50), nullable=False)
    annual_income = Column(Float, nullable=False)
    land_ownership = Column(Boolean, default=False)
    land_area_acres = Column(Float, default=0.0)
    category = Column(String(10), nullable=False)  # SC, ST, OBC, General, EWS
    family_size = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="profile")


class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(String, primary_key=True)
    name = Column(String(500), nullable=False)
    ministry = Column(String(500), nullable=False)
    category = Column(String(100), nullable=False)
    income_limit = Column(Float, nullable=True)
    land_required = Column(Boolean, default=False)
    land_area_min_acres = Column(Float, default=0.0)
    land_area_max_acres = Column(Float, nullable=True)
    benefit_amount = Column(Float, nullable=False)
    benefit_frequency = Column(String(50), default="One-time")
    benefit_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    documents_required = Column(JSON, default=list)
    eligibility_rules = Column(JSON, default=dict)
    application_link = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    applications = relationship("Application", back_populates="scheme")


class Application(Base):
    __tablename__ = "applications"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    scheme_id = Column(String, ForeignKey("schemes.id"), nullable=False)
    status = Column(String(20), default="Applied")  # Applied, In Progress, Approved, Rejected
    reference_no = Column(String(50), unique=True, nullable=False)
    applied_date = Column(DateTime, default=datetime.utcnow)
    expected_credit_date = Column(DateTime, nullable=True)
    benefit_amount = Column(Float, default=0.0)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="applications")
    scheme = relationship("Scheme", back_populates="applications")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    messages = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
