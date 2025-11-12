"""
Product Model - Quản lý sản phẩm
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class ProductCategory(Base):
    """Danh mục sản phẩm"""

    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    products = relationship("Product", back_populates="category")


class Product(Base):
    """Sản phẩm"""

    __tablename__ = "products"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Basic Info
    sku = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Category
    category_id = Column(Integer, ForeignKey("product_categories.id"))

    # Pricing
    unit_price = Column(Float, nullable=False)  # Giá bán
    cost_price = Column(Float)  # Giá vốn

    # Unit
    unit = Column(String(20), default="pcs")  # VD: pcs, kg, liter, box

    # Stock Control
    min_stock = Column(Integer, default=0)  # Tồn kho tối thiểu
    max_stock = Column(Integer)  # Tồn kho tối đa

    # Status
    is_active = Column(Boolean, default=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("ProductCategory", back_populates="products")
    batches = relationship("Batch", back_populates="product")
    stocks = relationship("Stock", back_populates="product")
