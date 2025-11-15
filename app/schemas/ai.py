from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ChatRequest(BaseModel):
    message: str = Field(..., description="User's message", min_length=1)

    class Config:
        json_schema_extra = {"example": {"message": "Đơn hàng của tôi đang ở đâu?"}}


class ChatResponse(BaseModel):
    intent: str
    response: str
    data: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "intent": "get_orders",
                "response": "Bạn có 5 đơn hàng. Đơn hàng mới nhất đang được giao.",
                "data": {"orders_count": 5, "latest_order_status": "Đang giao hàng"},
            }
        }


class IntentListResponse(BaseModel):
    intents: Dict[str, str]

    class Config:
        json_schema_extra = {
            "example": {
                "intents": {
                    "get_orders": "Truy vấn thông tin đơn hàng",
                    "check_stock": "Kiểm tra tồn kho sản phẩm",
                }
            }
        }
