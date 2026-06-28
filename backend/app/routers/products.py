"""Products router for SBI cross-sell recommendations."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, Profile, Application
from app.core.security import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/products", tags=["Products"])

class SBIProduct(BaseModel):
    id: str
    name: str
    description: str
    icon_type: str
    cta_text: str
    cta_link: str

# Master list of SBI products
SBI_PRODUCTS = {
    "kcc": SBIProduct(
        id="kcc",
        name="SBI Kisan Credit Card",
        description="Get timely credit for your agricultural needs at low interest rates.",
        icon_type="agriculture",
        cta_text="Apply for KCC",
        cta_link="https://sbi.co.in/web/agri-rural/agriculture-banking/crop-loan/kisan-credit-card"
    ),
    "home_loan": SBIProduct(
        id="home_loan",
        name="SBI Home Loan",
        description="Build your dream home with low EMIs. PMAY subsidy applicable.",
        icon_type="home",
        cta_text="Calculate EMI",
        cta_link="https://homeloans.sbi/"
    ),
    "micro_insurance": SBIProduct(
        id="micro_insurance",
        name="SBI General Micro Insurance",
        description="Affordable health and life coverage starting at just ₹1/day.",
        icon_type="shield",
        cta_text="View Plans",
        cta_link="https://www.sbilife.co.in/en/individual-life-insurance/micro-insurance"
    ),
    "mudra_loan": SBIProduct(
        id="mudra_loan",
        name="SBI e-Mudra Loan",
        description="Instant collateral-free business loan up to ₹50,000 for your shop.",
        icon_type="briefcase",
        cta_text="Get e-Mudra",
        cta_link="https://emudra.sbi.co.in:8044/emudra"
    ),
    "gold_loan": SBIProduct(
        id="gold_loan",
        name="SBI Agri Gold Loan",
        description="Quick funds against your gold ornaments with low processing fees.",
        icon_type="coins",
        cta_text="Check Rates",
        cta_link="https://sbi.co.in/web/agri-rural/agriculture-banking/gold-loan"
    )
}

@router.get("/recommendations", response_model=list[SBIProduct])
async def get_product_recommendations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Suggest SBI products based on user profile and active applications."""
    # Fetch profile
    result = await db.execute(select(Profile).where(Profile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    
    # Fetch applications
    app_result = await db.execute(select(Application.scheme_id).where(Application.user_id == current_user.id))
    applied_schemes = [row[0] for row in app_result.all()]
    
    recommendations = []
    recommended_ids = set()
    
    def add_recommendation(product_id: str):
        if product_id not in recommended_ids:
            recommendations.append(SBI_PRODUCTS[product_id])
            recommended_ids.add(product_id)

    if profile:
        # Rule 1: Farmers get KCC and Agri Gold Loan
        if profile.occupation == "Farmer" or profile.land_ownership:
            add_recommendation("kcc")
            add_recommendation("gold_loan")
            
        # Rule 2: Self-employed get Mudra
        if profile.occupation == "Self-Employed":
            add_recommendation("mudra_loan")
            
        # Rule 3: Low income gets Micro Insurance
        if profile.annual_income < 300000:
            add_recommendation("micro_insurance")

    # Rule 4: Scheme specific cross-sell
    if "pmay-gramin" in applied_schemes or "pmay-urban" in applied_schemes:
        add_recommendation("home_loan")
        
    if "pm-kisan-samman-nidhi" in applied_schemes:
        add_recommendation("kcc")
        
    if "pmjdy" in applied_schemes or "ayushman-bharat-pmjay" in applied_schemes:
        add_recommendation("micro_insurance")
        
    # Default fallback if no specific rules match
    if not recommendations:
        add_recommendation("micro_insurance")
        add_recommendation("gold_loan")

    # Return top 3 recommendations
    return recommendations[:3]
