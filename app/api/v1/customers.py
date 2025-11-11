"""
Customers API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.schemas.customer import Customer, CustomerCreate, CustomerUpdate
from app.schemas.common import PaginatedResponse
from app.services.customer_service import CustomerService
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.models.user import User as UserModel

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post(
    "/",
    response_model=Customer,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission("orders:create")],  # ← FIX: Bỏ Depends()
)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Tạo customer mới"""
    # Check duplicate email
    if customer.email:
        from app.models.customer import Customer as CustomerModel

        existing = (
            db.query(CustomerModel)
            .filter(CustomerModel.email == customer.email)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {customer.email} đã tồn tại",
            )

    return CustomerService.create_customer(db, customer)


@router.get(
    "/",
    response_model=PaginatedResponse[Customer],
    dependencies=[require_permission("orders:read")],  # ← FIX
)
def get_customers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    customer_type: Optional[str] = Query(default=None, pattern="^(b2c|b2b)$"),
    is_active: Optional[bool] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Lấy danh sách customers"""
    skip = (page - 1) * page_size

    customers, total = CustomerService.get_customers(
        db=db,
        skip=skip,
        limit=page_size,
        search=search,
        customer_type=customer_type,
        is_active=is_active,
    )

    return PaginatedResponse.create(
        items=customers, total=total, page=page, page_size=page_size
    )


@router.get(
    "/{customer_id}",
    response_model=Customer,
    dependencies=[require_permission("orders:read")],  # ← FIX
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Lấy thông tin customer theo ID"""
    customer = CustomerService.get_customer_by_id(db, customer_id)

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer với ID {customer_id} không tồn tại",
        )

    return customer


@router.put(
    "/{customer_id}",
    response_model=Customer,
    dependencies=[require_permission("orders:update")],  # ← FIX
)
def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Cập nhật thông tin customer"""
    customer = CustomerService.update_customer(db, customer_id, customer_update)

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer với ID {customer_id} không tồn tại",
        )

    return customer


@router.delete(
    "/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[require_permission("orders:delete")],  # ← FIX
)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Xóa (vô hiệu hóa) customer"""
    success = CustomerService.delete_customer(db, customer_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer với ID {customer_id} không tồn tại",
        )

    return None
