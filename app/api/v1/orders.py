"""
Orders API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.schemas.order import (
    Order,
    OrderCreate,
    OrderUpdate,
    OrderStatusUpdate,
    OrderWithItems,
    OrderWithDetails,
)
from app.schemas.common import PaginatedResponse
from app.services.order_service import OrderService
from app.services.customer_service import CustomerService
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.models.user import User as UserModel

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post(
    "/",
    response_model=OrderWithItems,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission("orders:create")],  # ← FIX
)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Tạo đơn hàng mới"""
    customer = CustomerService.get_customer_by_id(db, order.customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer với ID {order.customer_id} không tồn tại",
        )

    if not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Customer đã bị vô hiệu hóa"
        )

    return OrderService.create_order(db, order, current_user.id)


@router.get(
    "/",
    response_model=PaginatedResponse[Order],
    dependencies=[require_permission("orders:read")],  # ← FIX
)
def get_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    order_type: Optional[str] = Query(default=None, pattern="^(b2c|b2b)$"),
    customer_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Lấy danh sách đơn hàng"""
    skip = (page - 1) * page_size

    orders, total = OrderService.get_orders(
        db=db,
        skip=skip,
        limit=page_size,
        search=search,
        status=status,
        order_type=order_type,
        customer_id=customer_id,
    )

    return PaginatedResponse.create(
        items=orders, total=total, page=page, page_size=page_size
    )


@router.get(
    "/{order_id}",
    response_model=OrderWithItems,
    dependencies=[require_permission("orders:read")],  # ← FIX
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Lấy chi tiết đơn hàng theo ID"""
    order = OrderService.get_order_by_id(db, order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order với ID {order_id} không tồn tại",
        )

    return order


@router.patch(
    "/{order_id}/status",
    response_model=Order,
    dependencies=[require_permission("orders:update")],  # ← FIX
)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Cập nhật trạng thái đơn hàng"""
    order = OrderService.update_order_status(
        db, order_id, status_update, current_user.id
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order với ID {order_id} không tồn tại",
        )

    return order


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[require_permission("orders:delete")],  # ← FIX
)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Hủy đơn hàng (Cancel)"""
    status_update = OrderStatusUpdate(
        status="cancelled", note=f"Order cancelled by {current_user.username}"
    )

    order = OrderService.update_order_status(
        db, order_id, status_update, current_user.id
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order với ID {order_id} không tồn tại",
        )

    return None
