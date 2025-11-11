"""
Order Models - Quản lý đơn hàng B2C/B2B
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    Enum,
    Text,
    Boolean,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class OrderStatus(str, enum.Enum):
    """Trạng thái đơn hàng"""

    DRAFT = "draft"  # Nháp
    PENDING = "pending"  # Chờ xác nhận
    CONFIRMED = "confirmed"  # Đã xác nhận
    PROCESSING = "processing"  # Đang xử lý
    READY = "ready"  # Sẵn sàng giao
    SHIPPED = "shipped"  # Đang giao
    DELIVERED = "delivered"  # Đã giao
    CANCELLED = "cancelled"  # Đã hủy
    RETURNED = "returned"  # Đã trả hàng


class OrderType(str, enum.Enum):
    """Loại đơn hàng"""

    B2C = "b2c"  # Bán lẻ
    B2B = "b2b"  # Bán sỉ


class PaymentMethod(str, enum.Enum):
    """Phương thức thanh toán"""

    CASH = "cash"  # Tiền mặt
    BANK_TRANSFER = "transfer"  # Chuyển khoản
    CREDIT = "credit"  # Công nợ (B2B)


class Order(Base):
    __tablename__ = "orders"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Order Info
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    order_type = Column(Enum(OrderType), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.DRAFT, nullable=False)

    # Customer Info
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    # Financial Info
    subtotal = Column(Float, default=0)  # Tổng tiền hàng
    discount_amount = Column(Float, default=0)  # Giảm giá
    tax_amount = Column(Float, default=0)  # Thuế VAT
    shipping_fee = Column(Float, default=0)  # Phí vận chuyển
    total_amount = Column(Float, nullable=False)  # Tổng cộng

    # Payment Info
    payment_method = Column(Enum(PaymentMethod))
    payment_status = Column(String(20), default="unpaid")  # unpaid, partial, paid
    paid_amount = Column(Float, default=0)

    # Shipping Info
    shipping_address = Column(Text)
    shipping_city = Column(String(100))
    shipping_district = Column(String(100))
    shipping_note = Column(Text)

    # Internal Notes
    internal_note = Column(Text)  # Ghi chú nội bộ

    # Audit
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    confirmed_at = Column(DateTime)
    shipped_at = Column(DateTime)
    delivered_at = Column(DateTime)

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    status_logs = relationship(
        "OrderStatusLog", back_populates="order", cascade="all, delete-orphan"
    )
    created_by_user = relationship("User", foreign_keys=[created_by])


class OrderItem(Base):
    """Chi tiết sản phẩm trong đơn hàng"""

    __tablename__ = "order_items"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, nullable=False)  # Sẽ link tới Products sau

    # Product Info (snapshot tại thời điểm đặt hàng)
    product_name = Column(String(200), nullable=False)
    product_sku = Column(String(50))

    # Pricing
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    discount_percent = Column(Float, default=0)
    discount_amount = Column(Float, default=0)
    subtotal = Column(Float, nullable=False)  # unit_price * quantity - discount

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="items")


class OrderStatusLog(Base):
    """Lịch sử thay đổi trạng thái đơn hàng"""

    __tablename__ = "order_status_logs"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)

    # Status Change Info
    from_status = Column(String(20))
    to_status = Column(String(20), nullable=False)
    note = Column(Text)

    # Audit
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="status_logs")
    changed_by_user = relationship("User", foreign_keys=[changed_by])
