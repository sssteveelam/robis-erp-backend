"""
Products API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.schemas.product import (
    Product,
    ProductCreate,
    ProductUpdate,
    ProductWithCategory,
    ProductCategory,
    ProductCategoryCreate,
    ProductCategoryUpdate,
)
from app.schemas.common import PaginatedResponse
from app.services.product_service import ProductService, ProductCategoryService
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.models.user import User as UserModel

router = APIRouter(tags=["Products"])


# ============= PRODUCT CATEGORIES =============


@router.post(
    "/categories",
    response_model=ProductCategory,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        require_permission("inventory:manage")
    ],  # ← FIX: Dùng inventory:manage thay vì categories:create
)
def create_category(
    category: ProductCategoryCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Tạo category mới

    Permission: inventory:manage
    Roles: WAREHOUSE_STAFF, ADMIN
    """
    return ProductCategoryService.create_category(db, category)


@router.get(
    "/categories",
    response_model=PaginatedResponse[ProductCategory],
    dependencies=[
        require_permission("products:read")
    ],  # ← OK: Ai có products:read đều xem được
)
def get_categories(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=100),
    is_active: Optional[bool] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Lấy danh sách categories

    Permission: products:read
    Roles: Tất cả authenticated users
    """
    skip = (page - 1) * page_size

    categories, total = ProductCategoryService.get_categories(
        db=db, skip=skip, limit=page_size, is_active=is_active
    )

    return PaginatedResponse.create(
        items=categories, total=total, page=page, page_size=page_size
    )


# ============= PRODUCTS =============


@router.post(
    "/products",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission("products:create")],
)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Tạo product mới

    Permission: products:create
    Roles: WAREHOUSE_STAFF, ADMIN
    """
    try:
        return ProductService.create_product(db, product)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/products",
    response_model=PaginatedResponse[Product],
    dependencies=[require_permission("products:read")],
)
def get_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: Optional[str] = Query(default=None),
    category_id: Optional[int] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Lấy danh sách products

    Permission: products:read
    Roles: Tất cả authenticated users
    """
    skip = (page - 1) * page_size

    products, total = ProductService.get_products(
        db=db,
        skip=skip,
        limit=page_size,
        search=search,
        category_id=category_id,
        is_active=is_active,
    )

    return PaginatedResponse.create(
        items=products, total=total, page=page, page_size=page_size
    )


@router.get(
    "/products/{product_id}",
    response_model=Product,
    dependencies=[require_permission("products:read")],
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Lấy thông tin product theo ID

    Permission: products:read
    """
    product = ProductService.get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product với ID {product_id} không tồn tại",
        )

    return product


@router.put(
    "/products/{product_id}",
    response_model=Product,
    dependencies=[require_permission("products:update")],
)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Cập nhật product

    Permission: products:update
    Roles: WAREHOUSE_STAFF, ADMIN
    """
    product = ProductService.update_product(db, product_id, product_update)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product với ID {product_id} không tồn tại",
        )

    return product


@router.get(
    "/products/low-stock",
    response_model=list[Product],
    dependencies=[require_permission("products:read")],
)
def get_low_stock_products(
    db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)
):
    """
    Lấy danh sách products có tồn kho thấp hơn min_stock

    Permission: products:read
    Roles: Tất cả authenticated users
    """
    return ProductService.check_low_stock(db)
