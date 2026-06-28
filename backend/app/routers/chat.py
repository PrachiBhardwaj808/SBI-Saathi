"""Mock AI Chatbot endpoint."""

import asyncio
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, Profile
from app.schemas import ChatRequest, ChatMessageResponse
from app.core.security import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatMessageResponse)
async def chat_with_ai(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Simulate an AI conversation. Uses the user's profile context to give personalized responses.
    No real LLM is called in this phase to save on API keys.
    """
    # Fetch profile context
    result = await db.execute(select(Profile).where(Profile.user_id == current_user.id))
    profile = result.scalar_one_or_none()

    # Simulate network delay for AI thinking
    await asyncio.sleep(1.5)

    msg = request.message.lower()
    is_hindi = request.language == "hi"

    # Define mock logic based on profile and message
    reply = ""
    suggested = []

    if profile:
        if "apply" in msg or "kaise" in msg or "application" in msg:
            if is_hindi:
                reply = f"नमस्ते {profile.full_name}! आप योजना के कार्ड पर 'Apply Now' बटन पर क्लिक करके आवेदन कर सकते हैं। चूंकि आप {profile.state} से हैं, इसलिए आपको अपना आधार और आय प्रमाण पत्र चाहिए होगा।"
                suggested = ["मुझे कौन से दस्तावेज़ चाहिए?", "आवेदन की स्थिति कैसे जांचें?"]
            else:
                reply = f"Hello {profile.full_name}! You can apply by clicking the 'Apply Now' button on any scheme card on your dashboard. Since you are from {profile.state}, you will need your Aadhaar and Income Certificate."
                suggested = ["What documents do I need?", "How to check status?"]
                
        elif "eligible" in msg or "yojana" in msg or "scheme" in msg:
            if is_hindi:
                reply = f"आपकी आय (₹{profile.annual_income}) और व्यवसाय ({profile.occupation}) के आधार पर, आप PM Kisan और Ayushman Bharat जैसी योजनाओं के लिए पात्र हो सकते हैं। कृपया सटीक सूची के लिए डैशबोर्ड देखें।"
                suggested = ["PM Kisan क्या है?", "मेरी कुल लाभ राशि क्या है?"]
            else:
                reply = f"Based on your income (₹{profile.annual_income}) and occupation ({profile.occupation}), you might be eligible for schemes like PM Kisan and Ayushman Bharat. Please check the dashboard for the exact list."
                suggested = ["What is PM Kisan?", "What is my total benefit amount?"]
        else:
            if is_hindi:
                reply = f"नमस्ते {profile.full_name}! मैं SBI Saathi हूँ, आपका सरकारी योजना सहायक। मैं योजनाओं को खोजने और आवेदन करने में आपकी मदद कर सकता हूँ। आप क्या जानना चाहेंगे?"
                suggested = ["मैं किन योजनाओं के लिए पात्र हूँ?", "PM Kisan के बारे में बताएं"]
            else:
                reply = f"Hello {profile.full_name}! I am SBI Saathi, your government scheme assistant. I can help you find and apply for schemes. What would you like to know?"
                suggested = ["What schemes am I eligible for?", "Tell me about PM Kisan"]
    else:
        # Fallback if profile not complete
        if is_hindi:
            reply = "नमस्ते! मुझे आपकी मदद करने में खुशी होगी, लेकिन सबसे पहले आपको सटीक जानकारी के लिए अपना प्रोफाइल पूरा करना होगा।"
            suggested = ["प्रोफाइल कैसे पूरा करें?"]
        else:
            reply = "Hello! I'd love to help, but you need to complete your profile first so I can give you accurate information."
            suggested = ["How to complete profile?"]

    return ChatMessageResponse(
        reply=reply,
        suggested_questions=suggested,
        session_id=request.session_id or "new-session"
    )
