"""
Inventory Schemas - Batch, Stock, Movement, QC
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, date


# ============= WAREHOUSE =============


class WarehouseBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    address: Optional[str] = None


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    address: Optional[str] = None
    is_active: Optional[bool] = None


class Warehouse(WarehouseBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============= BATCH =============


class BatchBase(BaseModel):
    product_id: int
    initial_quantity: float = Field(..., gt=0)
    manufacturing_date: Optional[date] = None
    expiry_date: Optional[date] = None


class BatchCreate(BatchBase):
    @validator("expiry_date")
    def validate_expiry_date(cls, v, values):
        if v and "manufacturing_date" in values and values["manufacturing_date"]:
            if v <= values["manufacturing_date"]:
                raise ValueError("Expiry date must be after manufacturing date")
        return v


class BatchUpdate(BaseModel):
    qc_status: Optional[str] = Field(None, pattern="^(pending|passed|failed)$")
    qc_note: Optional[str] = None
    is_active: Optional[bool] = None


class Batch(BatchBase):
    id: int
    batch_number: str
    current_quantity: float
    qc_status: str
    qc_note: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============= STOCK =============


class Stock(BaseModel):
    id: int
    warehouse_id: int
    product_id: int
    quantity: float
    updated_at: datetime

    class Config:
        from_attributes = True


class StockSummary(BaseModel):
    """Tổng hợp tồn kho theo sản phẩm"""

    product_id: int
    product_sku: str
    product_name: str
    total_quantity: float
    warehouses: list[dict]  # [{warehouse_id, warehouse_name, quantity}]


# ============= STOCK MOVEMENT =============


class StockMovementBase(BaseModel):
    movement_type: str = Field(..., pattern="^(import|export|check|transfer|adjust)$")
    product_id: int
    batch_id: Optional[int] = None
    warehouse_id: int
    quantity: float = Field(..., gt=0)
    reference_type: Optional[str] = Field(None, max_length=50)
    reference_id: Optional[int] = None
    note: Optional[str] = None


class StockMovementCreate(StockMovementBase):
    pass


class StockMovement(StockMovementBase):
    id: int
    movement_number: str
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class StockMovementWithDetails(StockMovement):
    """Stock Movement kèm thông tin chi tiết"""

    product: Optional[dict] = None
    batch: Optional[dict] = None
    warehouse: Optional[dict] = None
    created_by_user: Optional[dict] = None


# ============= QC CHECKPOINT =============


class QCCheckpointBase(BaseModel):
    checkpoint_type: str = Field(..., pattern="^(input|inprocess|output)$")
    batch_id: int
    status: str = Field(..., pattern="^(pending|passed|failed)$")
    score: Optional[float] = Field(None, ge=0, le=100)
    note: Optional[str] = None
    defect_count: int = Field(default=0, ge=0)
    defect_description: Optional[str] = None


class QCCheckpointCreate(QCCheckpointBase):
    pass


class QCCheckpoint(QCCheckpointBase):
    id: int
    inspector_id: int
    inspected_at: datetime

    class Config:
        from_attributes = True


class QCCheckpointWithDetails(QCCheckpoint):
    """QC Checkpoint kèm thông tin chi tiết"""

    batch: Optional[dict] = None
    inspector: Optional[dict] = None
