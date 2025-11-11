"""
Customer Schemas - Pydantic models cho validation & serialization
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class CustomerBase(BaseModel):
    """Base schema cho Customer"""

    customer_type: str = Field(..., pattern="^(b2c|b2b)$")
    name: str = Field(..., min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    company_name: Optional[str] = Field(None, max_length=200)
    tax_code: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=100)


class CustomerCreate(CustomerBase):
    """Schema cho tạo Customer mới"""

    pass


class CustomerUpdate(BaseModel):
    """Schema cho update Customer"""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    company_name: Optional[str] = Field(None, max_length=200)
    tax_code: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    district: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class Customer(CustomerBase):
    """Schema cho Customer response"""

    id: int
    customer_code: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
