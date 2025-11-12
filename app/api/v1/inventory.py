"""
Inventory API Endpoints - Warehouses, Batches, Stock, Movements
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.schemas.inventory import (
    Warehouse,
    WarehouseCreate,
    Batch,
    BatchCreate,
    BatchUpdate,
    Stock,
    StockSummary,
    StockMovement,
    StockMovementCreate,
    StockMovementWithDetails,
)
from app.schemas.common import PaginatedResponse
from app.services.inventory_service import (
    WarehouseService,
    BatchService,
    StockService,
    StockMovementService,
)
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.models.user import User as UserModel

router = APIRouter(tags=["Inventory"])


# ============= WAREHOUSES =============


@router.post(
    "/warehouses",
    response_model=Warehouse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission("inventory:manage")],
)
def create_warehouse(
    warehouse: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Tạo warehouse mới"""
    return WarehouseService.create_warehouse(db, warehouse)


@router.get(
    "/warehouses",
    response_model=list[Warehouse],
    dependencies=[require_permission("inventory:read")],
)
def get_warehouses(
    is_active: Optional[bool] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Lấy danh sách warehouses"""
    return WarehouseService.get_warehouses(db, is_active)


# ============= BATCHES =============


@router.post(
    "/batches",
    response_model=Batch,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission("inventory:manage")],
)
def create_batch(
    batch: BatchCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Tạo batch mới (lô hàng)

    Permission: inventory:manage
    Roles: WAREHOUSE_STAFF, ADMIN
    """
    return BatchService.create_batch(db, batch)


@router.get(
    "/batches",
    response_model=list[Batch],
    dependencies=[require_permission("inventory:read")],
)
def get_batches_by_product(
    product_id: int = Query(...),
    qc_status: Optional[str] = Query(default=None, pattern="^(pending|passed|failed)$"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Lấy batches theo product"""
    return BatchService.get_batches_by_product(db, product_id, qc_status)


@router.patch(
    "/batches/{batch_id}",
    response_model=Batch,
    dependencies=[require_permission("qc:perform")],
)
def update_batch_qc(
    batch_id: int,
    batch_update: BatchUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Cập nhật QC status của batch

    Permission: qc:perform
    Roles: QC_STAFF, ADMIN
    """
    from app.models.inventory import Batch

    db_batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not db_batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch với ID {batch_id} không tồn tại",
        )

    if batch_update.qc_status:
        db_batch.qc_status = batch_update.qc_status
    if batch_update.qc_note:
        db_batch.qc_note = batch_update.qc_note

    db.commit()
    db.refresh(db_batch)

    return db_batch


# ============= STOCK =============


@router.get(
    "/stock",
    response_model=list[Stock],
    dependencies=[require_permission("inventory:read")],
)
def get_stock(
    warehouse_id: Optional[int] = Query(default=None),
    product_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Lấy thông tin tồn kho

    Permission: inventory:read
    """
    from app.models.inventory import Stock

    query = db.query(Stock)

    if warehouse_id:
        query = query.filter(Stock.warehouse_id == warehouse_id)
    if product_id:
        query = query.filter(Stock.product_id == product_id)

    return query.all()


@router.get(
    "/stock/summary",
    response_model=list[StockSummary],
    dependencies=[require_permission("inventory:read")],
)
def get_stock_summary(
    product_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Tổng hợp tồn kho theo sản phẩm

    Permission: inventory:read
    """
    results = StockService.get_stock_summary(db, product_id)

    # Transform to StockSummary
    summary_list = []
    for row in results:
        summary_list.append(
            StockSummary(
                product_id=row[0],
                product_sku=row[1],
                product_name=row[2],
                total_quantity=row[3],
                warehouses=[],  # TODO: Add warehouse breakdown
            )
        )

    return summary_list


# ============= STOCK MOVEMENTS =============


@router.post(
    "/stock/import",
    response_model=StockMovement,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission("inventory:manage")],
)
def import_stock(
    movement: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Nhập kho

    Permission: inventory:manage
    Roles: WAREHOUSE_STAFF, ADMIN

    Flow:
    - Tạo stock movement
    - Cập nhật stock quantity
    - Cập nhật batch quantity (nếu có)
    """
    movement.movement_type = "import"

    try:
        return StockMovementService.import_stock(db, movement, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/stock/export",
    response_model=StockMovement,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission("inventory:manage")],
)
def export_stock(
    movement: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Xuất kho

    Permission: inventory:manage
    Roles: WAREHOUSE_STAFF, ADMIN

    Flow:
    - Kiểm tra đủ tồn kho
    - Tự động chọn batch theo FEFO (nếu không chỉ định)
    - Tạo stock movement
    - Cập nhật stock quantity
    - Cập nhật batch quantity
    """
    movement.movement_type = "export"

    try:
        return StockMovementService.export_stock(db, movement, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/stock/movements",
    response_model=PaginatedResponse[StockMovement],
    dependencies=[require_permission("inventory:read")],
)
def get_stock_movements(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    movement_type: Optional[str] = Query(default=None),
    product_id: Optional[int] = Query(default=None),
    warehouse_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Lấy lịch sử nhập/xuất/kiểm kho

    Permission: inventory:read
    """
    skip = (page - 1) * page_size

    movements, total = StockMovementService.get_movements(
        db=db,
        skip=skip,
        limit=page_size,
        movement_type=movement_type,
        product_id=product_id,
        warehouse_id=warehouse_id,
    )

    return PaginatedResponse.create(
        items=movements, total=total, page=page, page_size=page_size
    )
