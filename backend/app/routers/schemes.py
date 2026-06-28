"""Schemes router: query and browse government welfare schemes."""

import json
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Scheme
from app.schemas import SchemeResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/schemes", tags=["Schemes"])

SCHEMES_JSON_PATH = Path(__file__).parent.parent.parent / "data" / "schemes.json"


async def seed_schemes(db: AsyncSession):
    """Seed schemes from JSON file if the table is empty."""
    result = await db.execute(select(Scheme).limit(1))
    if result.scalar_one_or_none() is not None:
        logger.info("Schemes already seeded, skipping.")
        return

    if not SCHEMES_JSON_PATH.exists():
        logger.warning(f"Schemes JSON not found at {SCHEMES_JSON_PATH}")
        return

    with open(SCHEMES_JSON_PATH, "r", encoding="utf-8") as f:
        schemes_data = json.load(f)

    for s in schemes_data:
        scheme = Scheme(
            id=s["id"],
            name=s["name"],
            ministry=s["ministry"],
            category=s["category"],
            income_limit=s.get("income_limit"),
            land_required=s.get("land_required", False),
            land_area_min_acres=s.get("land_area_min_acres", 0),
            land_area_max_acres=s.get("land_area_max_acres"),
            benefit_amount=s.get("benefit_amount", 0),
            benefit_frequency=s.get("benefit_frequency", "One-time"),
            benefit_type=s.get("benefit_type", ""),
            description=s.get("description", ""),
            documents_required=s.get("documents_required", []),
            eligibility_rules=s.get("eligibility_rules", {}),
            application_link=s.get("application_link"),
            is_active=s.get("is_active", True),
        )
        db.add(scheme)

    await db.commit()
    logger.info(f"✅ Seeded {len(schemes_data)} schemes from JSON.")


@router.get("", response_model=list[SchemeResponse])
async def list_schemes(
    category: str | None = Query(None, description="Filter by category"),
    state: str | None = Query(None, description="Filter by state"),
    db: AsyncSession = Depends(get_db),
):
    """List all active schemes, with optional category/state filters."""
    query = select(Scheme).where(Scheme.is_active == True)

    if category and category != "All":
        query = query.where(Scheme.category == category)

    result = await db.execute(query)
    schemes = result.scalars().all()

    # If state filter is provided, further filter by eligibility_rules
    if state:
        schemes = [
            s for s in schemes
            if s.eligibility_rules.get("states_any", True)
            or state in s.eligibility_rules.get("states", [])
        ]

    return [SchemeResponse.model_validate(s) for s in schemes]


@router.get("/{scheme_id}", response_model=SchemeResponse)
async def get_scheme(scheme_id: str, db: AsyncSession = Depends(get_db)):
    """Get a single scheme by ID."""
    result = await db.execute(select(Scheme).where(Scheme.id == scheme_id))
    scheme = result.scalar_one_or_none()

    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    return SchemeResponse.model_validate(scheme)
