"""Eligibility router for checking scheme eligibility."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, Profile, Scheme
from app.schemas import EligibilityResponse
from app.core.security import get_current_user
from app.services.ai_engine import check_eligibility

router = APIRouter(prefix="/eligibility", tags=["Eligibility"])


@router.get("/check", response_model=EligibilityResponse)
async def run_eligibility_check(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run the AI eligibility engine for the current user."""
    # 1. Get user profile
    result = await db.execute(select(Profile).where(Profile.user_id == current_user.id))
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(status_code=400, detail="Profile not found. Please complete your profile first.")

    # 2. Get all active schemes
    result = await db.execute(select(Scheme).where(Scheme.is_active == True))
    schemes = result.scalars().all()

    if not schemes:
        return EligibilityResponse(
            eligible_schemes=[],
            total_potential_benefits=0,
            schemes_count=0
        )

    # 3. Run mock AI engine
    eligible_results, total_benefits = check_eligibility(profile, schemes)

    return EligibilityResponse(
        eligible_schemes=eligible_results,
        total_potential_benefits=total_benefits,
        schemes_count=len(eligible_results)
    )
