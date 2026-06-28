"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── Auth ──
class OTPRequest(BaseModel):
    mobile: str = Field(..., min_length=10, max_length=10, pattern=r"^\d{10}$")


class OTPVerifyRequest(BaseModel):
    mobile: str = Field(..., min_length=10, max_length=10)
    otp: str = Field(..., min_length=6, max_length=6)


class TokenResponse(BaseModel):
    token: str
    user: "UserResponse"


class UserResponse(BaseModel):
    id: str
    mobile: str
    email: Optional[str] = None
    is_verified: bool
    is_profile_complete: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Profile ──
class ProfileCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    age: int = Field(..., ge=18, le=100)
    gender: str = Field(..., pattern=r"^(Male|Female|Other)$")
    state: str = Field(..., min_length=2)
    district: str = Field(..., min_length=2)
    occupation: str
    annual_income: float = Field(..., ge=0)
    land_ownership: bool = False
    land_area_acres: float = Field(default=0.0, ge=0)
    category: str = Field(..., pattern=r"^(SC|ST|OBC|General|EWS)$")
    family_size: int = Field(default=1, ge=1, le=20)


class ProfileResponse(ProfileCreate):
    user_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    occupation: Optional[str] = None
    annual_income: Optional[float] = None
    land_ownership: Optional[bool] = None
    land_area_acres: Optional[float] = None
    category: Optional[str] = None
    family_size: Optional[int] = None


# ── Scheme ──
class SchemeResponse(BaseModel):
    id: str
    name: str
    ministry: str
    category: str
    income_limit: Optional[float] = None
    land_required: bool
    land_area_min_acres: float
    land_area_max_acres: Optional[float] = None
    benefit_amount: float
    benefit_frequency: str
    benefit_type: str
    description: str
    documents_required: list[str]
    eligibility_rules: dict
    application_link: Optional[str] = None
    is_active: bool

    model_config = {"from_attributes": True}


# ── Application ──
class ApplicationCreate(BaseModel):
    scheme_id: str


class ApplicationResponse(BaseModel):
    id: str
    user_id: str
    scheme_id: str
    scheme_name: str = ""
    status: str
    reference_no: str
    applied_date: datetime
    expected_credit_date: Optional[datetime] = None
    benefit_amount: float
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Eligibility ──
class EligibilityResult(BaseModel):
    scheme: SchemeResponse
    eligibility_status: str  # "Eligible", "Likely Eligible", "Not Eligible"
    reason: str
    benefit_amount: float
    confidence_score: float


class EligibilityResponse(BaseModel):
    eligible_schemes: list[EligibilityResult]
    total_potential_benefits: float
    schemes_count: int


# ── Chat ──
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    language: str = "en"
    session_id: Optional[str] = None


class ChatMessageResponse(BaseModel):
    reply: str
    suggested_questions: list[str]
    session_id: str


# ── Dashboard ──
class DashboardStats(BaseModel):
    total_potential_benefits: float = 0
    eligible_schemes_count: int = 0
    active_applications: int = 0
    approved_amount: float = 0
