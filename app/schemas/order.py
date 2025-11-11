"""
Order Schemas - Pydantic models cho Orders
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


# ============= ORDER ITEM SCHEMAS =============


class OrderItemBase(BaseModel):
    """Base schema cho OrderItem"""

    product_id: int
    product_name: str = Field(..., min_length=1, max_length=200)
    product_sku: Optional[str] = Field(None, max_length=50)
    unit_price: float = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    discount_percent: float = Field(default=0, ge=0, le=100)
    discount_amount: float = Field(default=0, ge=0)


class OrderItemCreate(BaseModel):
    """Schema cho tạo OrderItem"""

    product_id: int
    product_name: str
    product_sku: Optional[str] = None
    unit_price: float = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    discount_percent: float = Field(default=0, ge=0, le=100)


class OrderItem(OrderItemBase):
    """Schema cho OrderItem response"""

    id: int
    order_id: int
    subtotal: float
    created_at: datetime

    class Config:
        from_attributes = True


# ============= ORDER SCHEMAS =============


class OrderBase(BaseModel):
    """Base schema cho Order"""

    customer_id: int
    order_type: str = Field(..., pattern="^(b2c|b2b)$")
    shipping_address: Optional[str] = None
    shipping_city: Optional[str] = Field(None, max_length=100)
    shipping_district: Optional[str] = Field(None, max_length=100)
    shipping_note: Optional[str] = None
    internal_note: Optional[str] = None
    payment_method: Optional[str] = Field(None, pattern="^(cash|transfer|credit)$")


class OrderCreate(OrderBase):
    """Schema cho tạo Order mới"""

    items: List[OrderItemCreate] = Field(..., min_items=1)
    discount_amount: float = Field(default=0, ge=0)
    shipping_fee: float = Field(default=0, ge=0)

    @validator("items")
    def validate_items(cls, v):
        if not v:
            raise ValueError("Order phải có ít nhất 1 sản phẩm")
        return v


class OrderUpdate(BaseModel):
    """Schema cho update Order"""

    shipping_address: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_district: Optional[str] = None
    shipping_note: Optional[str] = None
    internal_note: Optional[str] = None
    payment_method: Optional[str] = Field(None, pattern="^(cash|transfer|credit)$")


class OrderStatusUpdate(BaseModel):
    """Schema cho cập nhật trạng thái Order"""

    status: str = Field(
        ...,
        pattern="^(draft|pending|confirmed|processing|ready|shipped|delivered|cancelled|returned)$",
    )
    note: Optional[str] = None


class Order(OrderBase):
    """Schema cho Order response"""

    id: int
    order_number: str
    status: str
    subtotal: float
    discount_amount: float
    tax_amount: float
    shipping_fee: float
    total_amount: float
    payment_status: str
    paid_amount: float
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderWithItems(Order):
    """Schema cho Order kèm danh sách items"""

    items: List[OrderItem] = []

    class Config:
        from_attributes = True


class OrderWithDetails(OrderWithItems):
    """Schema cho Order kèm đầy đủ thông tin"""

    customer: Optional[dict] = None  # Sẽ populate sau

    class Config:
        from_attributes = True


# ============= ORDER STATUS LOG SCHEMAS =============


class OrderStatusLog(BaseModel):
    """Schema cho OrderStatusLog"""

    id: int
    order_id: int
    from_status: Optional[str]
    to_status: str
    note: Optional[str]
    changed_by: int
    changed_at: datetime

    class Config:
        from_attributes = True
