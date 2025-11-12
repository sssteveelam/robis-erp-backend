"""
Inventory Models - Batch, Stock, StockMovement, QC
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
    Date,
)
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum
from app.db.database import Base


class Batch(Base):
    """Lô hàng"""

    __tablename__ = "batches"

    id = Column(Integer, primary_key=True, index=True)

    # Batch Info
    batch_number = Column(String(50), unique=True, index=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Quantity
    initial_quantity = Column(Float, nullable=False)  # Số lượng ban đầu
    current_quantity = Column(Float, nullable=False)  # Số lượng hiện tại

    # Dates
    manufacturing_date = Column(Date)
    expiry_date = Column(Date)

    # QC Status
    qc_status = Column(String(20), default="pending")  # pending, passed, failed
    qc_note = Column(Text)

    # Status
    is_active = Column(Boolean, default=True)

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    product = relationship("Product", back_populates="batches")
    stock_movements = relationship("StockMovement", back_populates="batch")


class Warehouse(Base):
    """Kho"""

    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    address = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    stocks = relationship("Stock", back_populates="warehouse")


class Stock(Base):
    """Tồn kho theo kho và sản phẩm"""

    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)

    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    quantity = Column(Float, default=0)  # Tổng tồn kho

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    warehouse = relationship("Warehouse", back_populates="stocks")
    product = relationship("Product", back_populates="stocks")


class MovementType(str, enum.Enum):
    """Loại phiếu kho"""

    IMPORT = "import"  # Nhập kho
    EXPORT = "export"  # Xuất kho
    CHECK = "check"  # Kiểm kho
    TRANSFER = "transfer"  # Chuyển kho
    ADJUST = "adjust"  # Điều chỉnh


class StockMovement(Base):
    """Nhập/Xuất/Kiểm kho"""

    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)

    # Movement Info
    movement_number = Column(String(50), unique=True, index=True, nullable=False)
    movement_type = Column(Enum(MovementType), nullable=False)

    # Product & Batch
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"))

    # Warehouse
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)

    # Quantity
    quantity = Column(Float, nullable=False)

    # Reference
    reference_type = Column(String(50))  # VD: "order", "purchase_order"
    reference_id = Column(Integer)  # ID của đơn liên quan

    # Notes
    note = Column(Text)

    # Audit
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    product = relationship("Product")
    batch = relationship("Batch", back_populates="stock_movements")
    warehouse = relationship("Warehouse")
    created_by_user = relationship("User", foreign_keys=[created_by])


class QCCheckpointType(str, enum.Enum):
    """Điểm kiểm QC"""

    INPUT = "input"  # Kiểm đầu vào (nguyên liệu)
    INPROCESS = "inprocess"  # Kiểm trong quá trình
    OUTPUT = "output"  # Kiểm đầu ra (thành phẩm)


class QCCheckpoint(Base):
    """Điểm kiểm QC"""

    __tablename__ = "qc_checkpoints"

    id = Column(Integer, primary_key=True, index=True)

    # QC Info
    checkpoint_type = Column(Enum(QCCheckpointType), nullable=False)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=False)

    # Results
    status = Column(String(20), nullable=False)  # passed, failed, pending
    score = Column(Float)  # Điểm đánh giá (0-100)
    note = Column(Text)

    # Defects
    defect_count = Column(Integer, default=0)
    defect_description = Column(Text)

    # Inspector
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    inspected_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    batch = relationship("Batch")
    inspector = relationship("User", foreign_keys=[inspector_id])
