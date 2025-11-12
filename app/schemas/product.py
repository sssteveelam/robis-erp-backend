"""
Product Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ============= PRODUCT CATEGORY =============


class ProductCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class ProductCategoryCreate(ProductCategoryBase):
    pass


class ProductCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProductCategory(ProductCategoryBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============= PRODUCT =============


class ProductBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    category_id: Optional[int] = None
    unit_price: float = Field(..., gt=0)
    cost_price: Optional[float] = Field(None, ge=0)
    unit: str = Field(default="pcs", max_length=20)
    min_stock: int = Field(default=0, ge=0)
    max_stock: Optional[int] = Field(None, ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    category_id: Optional[int] = None
    unit_price: Optional[float] = Field(None, gt=0)
    cost_price: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=20)
    min_stock: Optional[int] = Field(None, ge=0)
    max_stock: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class Product(ProductBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProductWithCategory(Product):
    category: Optional[ProductCategory] = None

    class Config:
        from_attributes = True
