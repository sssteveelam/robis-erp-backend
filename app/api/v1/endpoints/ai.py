from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import os
import logging

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.ai_chatbot_service import RobisAIChatbot

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=500)


class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float


class HealthResponse(BaseModel):
    status: str
    gemini_configured: bool
    model: str


@router.post("/ai/chat", response_model=ChatResponse)
def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Chat với AI Assistant"""
    try:
        chatbot = RobisAIChatbot(db, current_user)
        result = chatbot.chat(request.message)

        return ChatResponse(
            response=result["response"],
            intent=result["intent"],
            confidence=result["confidence"],
        )
    except ValueError as e:
        logger.error(f"AI config error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI configuration error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"AI error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI error: {str(e)}",
        )


@router.get("/ai/health", response_model=HealthResponse)
def check_ai_health():
    """Check AI service status"""
    api_key = os.getenv("GOOGLE_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    return HealthResponse(
        status="healthy" if api_key else "unhealthy",
        gemini_configured=bool(api_key),
        model=model,
    )
