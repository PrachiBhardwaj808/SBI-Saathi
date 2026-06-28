"""Profile router: CRUD operations for user profiles."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, Profile
from app.schemas import ProfileCreate, ProfileResponse, ProfileUpdate
from app.core.security import get_current_user

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.post("", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_profile(
    profile_data: ProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create or update the user's profile (upsert)."""
    result = await db.execute(
        select(Profile).where(Profile.user_id == current_user.id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Update existing profile
        for field, value in profile_data.model_dump().items():
            setattr(existing, field, value)
        await db.commit()
        await db.refresh(existing)
        profile = existing
    else:
        # Create new profile
        profile = Profile(user_id=current_user.id, **profile_data.model_dump())
        db.add(profile)
        await db.commit()
        await db.refresh(profile)

    # Mark user as profile complete
    current_user.is_profile_complete = True
    await db.commit()

    return ProfileResponse.model_validate(profile)


@router.get("", response_model=ProfileResponse)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the current user's profile."""
    result = await db.execute(
        select(Profile).where(Profile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please complete your profile.",
        )

    return ProfileResponse.model_validate(profile)


@router.put("", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update specific fields of the user's profile."""
    result = await db.execute(
        select(Profile).where(Profile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found.",
        )

    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    return ProfileResponse.model_validate(profile)
