from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.schemas.role import Permission, PermissionCreate, PermissionUpdate
from app.schemas.common import PaginatedResponse
from app.services.role_service import PermissionService
from app.api.dependencies.auth import get_current_active_superuser
from app.models.user import User as UserModel

router = APIRouter(prefix="/permissions", tags=["Permission Management"])


@router.get("/", response_model=PaginatedResponse[Permission])
def get_permissions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    resource: Optional[str] = Query(default=None, description="Filter by resource"),
    action: Optional[str] = Query(default=None, description="Filter by action"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """
    **Lấy danh sách permissions (chỉ superuser)**

    - Pagination và filtering
    - Filter theo resource (users, orders, products...)
    - Filter theo action (create, read, update, delete...)
    """
    skip = (page - 1) * page_size

    permissions, total = PermissionService.get_permissions(
        db=db, skip=skip, limit=page_size, resource=resource, action=action
    )

    return PaginatedResponse.create(
        items=permissions, total=total, page=page, page_size=page_size
    )


@router.post("/", response_model=Permission, status_code=status.HTTP_201_CREATED)
def create_permission(
    permission: PermissionCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """
    **Tạo permission mới (chỉ superuser)**

    - name: Unique, format "resource:action" (VD: "users:create")
    - resource: Resource name (VD: "users", "orders")
    - action: Action (VD: "create", "read", "update", "delete")
    """
    # Check duplicate name
    existing_perm = PermissionService.get_permission_by_name(db, name=permission.name)
    if existing_perm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Permission with name '{permission.name}' already exists",
        )

    return PermissionService.create_permission(db, permission=permission)


@router.get("/{permission_id}", response_model=Permission)
def get_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """
    **Lấy chi tiết permission**
    """
    permission = PermissionService.get_permission(db, permission_id=permission_id)

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission with id {permission_id} not found",
        )

    return permission


@router.put("/{permission_id}", response_model=Permission)
def update_permission(
    permission_id: int,
    permission_update: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """
    **Update permission (chỉ description)**

    - Không cho phép đổi name, resource, action (tránh conflict)
    """
    updated_permission = PermissionService.update_permission(
        db, permission_id=permission_id, permission_update=permission_update
    )

    if not updated_permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission with id {permission_id} not found",
        )

    return updated_permission


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """
    **Xóa permission**

    - Xóa luôn associations với roles
    """
    success = PermissionService.delete_permission(db, permission_id=permission_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Permission with id {permission_id} not found",
        )

    return None
