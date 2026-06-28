"""Authentication router: OTP-based login/signup flow."""

import random
import time
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.schemas import OTPRequest, OTPVerifyRequest, TokenResponse, UserResponse
from app.core.security import create_access_token, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ── In-memory OTP store: { mobile: { otp, expires_at } } ──
_otp_store: dict[str, dict] = {}
OTP_EXPIRY_SECONDS = 300  # 5 minutes


@router.post("/send-otp")
async def send_otp(request: OTPRequest):
    """Generate and 'send' a 6-digit OTP. Logs to console for demo."""
    otp = f"{random.randint(100000, 999999)}"
    _otp_store[request.mobile] = {
        "otp": otp,
        "expires_at": time.time() + OTP_EXPIRY_SECONDS,
    }

    # In production, send via SMS gateway. For demo, log to console.
    logger.info(f"📱 OTP for +91{request.mobile}: {otp}")
    print(f"\n{'='*40}")
    print(f"  📱 OTP for +91{request.mobile}: {otp}")
    print(f"{'='*40}\n")

    return {
        "message": "OTP sent successfully",
        "otp_for_demo": otp,  # Only for demo/prototype — remove in production
    }


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(
    request: OTPVerifyRequest,
    db: AsyncSession = Depends(get_db),
):
    """Verify OTP and return JWT token. Creates user if new."""
    stored = _otp_store.get(request.mobile)

    if not stored:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No OTP found. Please request a new one.",
        )

    if time.time() > stored["expires_at"]:
        del _otp_store[request.mobile]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new one.",
        )

    if stored["otp"] != request.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP. Please try again.",
        )

    # OTP verified — clean up
    del _otp_store[request.mobile]

    # Find or create user
    result = await db.execute(select(User).where(User.mobile == request.mobile))
    user = result.scalar_one_or_none()

    if not user:
        user = User(mobile=request.mobile, is_verified=True)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"✅ New user created: {request.mobile}")
    else:
        if not user.is_verified:
            user.is_verified = True
            await db.commit()
            await db.refresh(user)

    # Generate JWT
    token = create_access_token(data={"sub": user.id})

    return TokenResponse(
        token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Return current authenticated user info."""
    return UserResponse.model_validate(current_user)
