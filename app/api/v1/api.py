"""
AI Chatbot API Endpoints
Google Gemini Integration for Robis ERP
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Dict, Any
import os

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.ai_chatbot_service import RobisAIChatbot

router = APIRouter()


# Schemas
class ChatRequest(BaseModel):
    """Chat request schema"""

    message: str = Field(..., min_length=1, max_length=500, description="User message")

    model_config = {
        "json_schema_extra": {
            "examples": [{"message": "Hôm nay có bao nhiêu đơn hàng?"}]
        }
    }


class ChatResponse(BaseModel):
    """Chat response schema"""

    response: str = Field(..., description="AI response message")
    intent: str = Field(..., description="Detected user intent")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Intent confidence score"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "response": "Hôm nay có 5 đơn hàng với tổng giá trị 15,000,000 VNĐ",
                    "intent": "get_orders",
                    "confidence": 0.95,
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = Field(..., description="Service status")
    gemini_configured: bool = Field(..., description="Gemini API configured")
    model: str = Field(..., description="Model name being used")


# Endpoints
@router.post(
    "/ai/chat",
    response_model=ChatResponse,
    summary="Chat với AI Assistant",
    description="""
    Gửi tin nhắn đến AI Assistant để nhận trợ giúp về:
    
    - **Đơn hàng**: "Hôm nay có bao nhiêu đơn?"
    - **Tồn kho**: "Sản phẩm SP-001 còn bao nhiêu?"
    - **Chấm công**: "Ai đi muộn hôm nay?"
    - **Nhân viên**: "Thông tin nhân viên Nguyễn Văn An"
    
    Yêu cầu authentication token.
    """,
)
def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Chat với AI Assistant

    **Authentication Required:** Bearer token

    **Rate Limit:** 100 requests/hour per user
    """
    try:
        # Initialize chatbot
        chatbot = RobisAIChatbot(db, current_user)

        # Process message
        result = chatbot.chat(request.message)

        return ChatResponse(
            response=result["response"],
            intent=result["intent"],
            confidence=result["confidence"],
        )

    except ValueError as e:
        # Configuration error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service configuration error: {str(e)}",
        )

    except Exception as e:
        # Other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI service error: {str(e)}",
        )


@router.get(
    "/ai/health",
    response_model=HealthResponse,
    summary="Kiểm tra trạng thái AI service",
    description="Check if AI service is properly configured and running",
)
def check_ai_health():
    """
    Kiểm tra trạng thái AI service

    **No Authentication Required**

    Returns:
    - **status**: healthy/unhealthy
    - **gemini_configured**: API key configured
    - **model**: Model name
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-pro")

    return HealthResponse(
        status="healthy" if api_key else "unhealthy",
        gemini_configured=bool(api_key),
        model=model,
    )


@router.get(
    "/ai/intents",
    summary="Danh sách intents được hỗ trợ",
    description="Lấy danh sách các intents (ý định) mà AI có thể xử lý",
)
def list_intents() -> Dict[str, Any]:
    """
    Danh sách intents được hỗ trợ

    **No Authentication Required**

    Returns dictionary với list intents và examples
    """
    return {
        "intents": [
            {
                "intent": "get_orders",
                "description": "Truy vấn thông tin đơn hàng",
                "examples": [
                    "Hôm nay có bao nhiêu đơn hàng?",
                    "Đơn hàng tuần này",
                    "Tổng giá trị đơn hàng hôm nay",
                ],
            },
            {
                "intent": "check_stock",
                "description": "Kiểm tra tồn kho sản phẩm",
                "examples": [
                    "Sản phẩm SP-001 còn bao nhiêu?",
                    "Kiểm tra kho hàng",
                    "Tồn kho sản phẩm XYZ",
                ],
            },
            {
                "intent": "check_attendance",
                "description": "Xem thông tin chấm công",
                "examples": [
                    "Ai đi muộn hôm nay?",
                    "Chấm công hôm nay",
                    "Nhân viên đi muộn",
                ],
            },
            {
                "intent": "employee_info",
                "description": "Tra cứu thông tin nhân viên",
                "examples": [
                    "Thông tin Nguyễn Văn An",
                    "Email của nhân viên A",
                    "Bộ phận của nhân viên B",
                ],
            },
            {
                "intent": "help",
                "description": "Hướng dẫn sử dụng AI assistant",
                "examples": ["Giúp tôi", "Bạn có thể làm gì?", "Hướng dẫn"],
            },
            {
                "intent": "general",
                "description": "Chào hỏi, cảm ơn, hội thoại thông thường",
                "examples": ["Xin chào", "Cảm ơn", "Tạm biệt"],
            },
        ],
        "total": 6,
    }
