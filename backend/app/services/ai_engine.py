"""Mock AI Eligibility Engine (Rule-based)."""

from typing import List, Tuple
from app.models import Profile, Scheme
from app.schemas import EligibilityResult, SchemeResponse


def check_eligibility(profile: Profile, schemes: List[Scheme]) -> Tuple[List[EligibilityResult], float]:
    """
    Evaluates a user profile against a list of schemes using rule-based filtering.
    Returns a tuple of (List of eligible schemes, Total potential benefits).
    """
    eligible_results = []
    total_benefits = 0.0

    for scheme in schemes:
        rules = scheme.eligibility_rules
        is_eligible = True
        reasons = []

        # 1. Check Occupation
        if rules.get("occupation"):
            if profile.occupation not in rules["occupation"]:
                is_eligible = False
            else:
                reasons.append(f"occupation as a {profile.occupation}")

        # 2. Check Land Requirements
        if rules.get("land_required"):
            if not profile.land_ownership:
                is_eligible = False
            else:
                if rules.get("min_land_area") and profile.land_area_acres < rules["min_land_area"]:
                    is_eligible = False
                if rules.get("max_land_area") and profile.land_area_acres > rules["max_land_area"]:
                    is_eligible = False
                if is_eligible:
                    reasons.append(f"agricultural land ownership of {profile.land_area_acres} acres")

        # 3. Check Income Limit
        if rules.get("max_income") is not None:
            if profile.annual_income > rules["max_income"]:
                is_eligible = False
            else:
                reasons.append(f"annual income falling within the ₹{rules['max_income']} limit")

        # 4. Check Category
        if not rules.get("category_any", True):
            if "categories" in rules and profile.category not in rules["categories"]:
                is_eligible = False
            else:
                reasons.append(f"category ({profile.category})")

        # 5. Check State
        if not rules.get("states_any", True):
            if "states" in rules and profile.state not in rules["states"]:
                is_eligible = False
            else:
                reasons.append(f"residence in {profile.state}")
                
        # 6. Check Age
        if rules.get("min_age") and profile.age < rules["min_age"]:
            is_eligible = False
        if rules.get("max_age") and profile.age > rules["max_age"]:
            is_eligible = False
        if is_eligible and (rules.get("min_age") or rules.get("max_age")):
             reasons.append(f"age ({profile.age} years)")

        # 7. Check Gender
        if rules.get("gender"):
            if profile.gender not in rules["gender"]:
                is_eligible = False
            else:
                reasons.append(f"gender ({profile.gender})")


        if is_eligible:
            # Construct AI-like reasoning string
            if reasons:
                if len(reasons) > 1:
                    reasons_str = ", ".join(reasons[:-1]) + ", and " + reasons[-1]
                else:
                    reasons_str = reasons[0]
                reasoning = f"Based on your profile, you qualify because of your {reasons_str}."
            else:
                reasoning = "Your profile meets all the general criteria for this scheme."

            # Calculate mock confidence score
            confidence = min(0.99, 0.85 + (len(reasons) * 0.03))

            eligible_results.append(
                EligibilityResult(
                    scheme=SchemeResponse.model_validate(scheme),
                    eligibility_status="Eligible",
                    reason=reasoning,
                    benefit_amount=scheme.benefit_amount,
                    confidence_score=round(confidence, 2),
                )
            )
            total_benefits += scheme.benefit_amount

    # Sort by confidence and benefit amount
    eligible_results.sort(key=lambda x: (x.confidence_score, x.benefit_amount), reverse=True)
    return eligible_results, total_benefits
