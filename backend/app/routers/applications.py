"""Applications router for scheme applications tracking."""

import random
import string
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, Application, Scheme
from app.schemas import ApplicationCreate, ApplicationResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/applications", tags=["Applications"])


def generate_reference_no() -> str:
    """Generate a realistic banking reference number (e.g., SBI-APP-2026-XYZ123)."""
    year = datetime.now().year
    random_str = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"SBI-APP-{year}-{random_str}"


async def update_simulated_status(app: Application, db: AsyncSession):
    """
    Simulate application processing based on time elapsed since submission.
    This creates a live-feel prototype without background workers.
    """
    if app.status == "Approved" or app.status == "Rejected":
        return app

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    applied = app.applied_date
    delta_minutes = (now - applied).total_seconds() / 60.0

    updated = False
    if app.status == "Applied" and delta_minutes > 1:
        app.status = "In Progress"
        updated = True
    
    if app.status == "In Progress" and delta_minutes > 3:
        # 90% chance of approval for demo purposes
        if random.random() < 0.9:
            app.status = "Approved"
            # Simulate a credit date 3 days from now
            app.expected_credit_date = now + timedelta(days=3)
        else:
            app.status = "Rejected"
            app.rejection_reason = "Document verification failed. Please visit nearest SBI branch."
        updated = True

    if updated:
        await db.commit()
        await db.refresh(app)
        
    return app


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    app_data: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit a new application for a scheme."""
    # Check if scheme exists
    result = await db.execute(select(Scheme).where(Scheme.id == app_data.scheme_id))
    scheme = result.scalar_one_or_none()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    # Check for existing application
    result = await db.execute(
        select(Application).where(
            Application.user_id == current_user.id,
            Application.scheme_id == app_data.scheme_id
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400, 
            detail="You have already applied for this scheme."
        )

    # Create new application
    new_app = Application(
        user_id=current_user.id,
        scheme_id=scheme.id,
        status="Applied",
        reference_no=generate_reference_no(),
        benefit_amount=scheme.benefit_amount
    )
    db.add(new_app)
    await db.commit()
    await db.refresh(new_app)

    # Inject scheme name for response
    app_dict = {c.name: getattr(new_app, c.name) for c in new_app.__table__.columns}
    app_dict["scheme_name"] = scheme.name

    return ApplicationResponse(**app_dict)


@router.get("", response_model=list[ApplicationResponse])
async def get_applications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all applications for the user, simulating status updates on read."""
    result = await db.execute(
        select(Application, Scheme.name.label("scheme_name"))
        .join(Scheme, Application.scheme_id == Scheme.id)
        .where(Application.user_id == current_user.id)
        .order_by(Application.created_at.desc())
    )
    rows = result.all()

    responses = []
    for app, scheme_name in rows:
        # Simulate status update
        app = await update_simulated_status(app, db)
        
        app_dict = {c.name: getattr(app, c.name) for c in app.__table__.columns}
        app_dict["scheme_name"] = scheme_name
        responses.append(ApplicationResponse(**app_dict))

    return responses
