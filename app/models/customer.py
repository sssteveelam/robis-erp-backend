"""
Customer Model - Quản lý thông tin khách hàng B2C/B2B
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class CustomerType(str, enum.Enum):
    """Loại khách hàng"""

    B2C = "b2c"  # Khách lẻ
    B2B = "b2b"  # Khách doanh nghiệp


class Customer(Base):
    __tablename__ = "customers"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Basic Info
    customer_code = Column(String(50), unique=True, index=True, nullable=False)
    customer_type = Column(Enum(CustomerType), nullable=False)
    name = Column(String(200), nullable=False)
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20))

    # B2B specific fields
    company_name = Column(String(200))  # Tên công ty (B2B)
    tax_code = Column(String(50))  # Mã số thuế (B2B)

    # Address
    address = Column(Text)
    city = Column(String(100))
    district = Column(String(100))

    # Status
    is_active = Column(Boolean, default=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    orders = relationship("Order", back_populates="customer")
