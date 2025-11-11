from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

# Database
from app.db.database import get_db

# Schemas - IMPORT TRƯỚC KHI DÙNG
from app.schemas.user import User, UserUpdate  # ← User schema (response model)
from app.schemas.role import Role, RoleAssignment
from app.schemas.common import PaginatedResponse

# Services
from app.services.user_service import UserService
from app.services.role_service import RoleService

# Dependencies
from app.api.dependencies.auth import get_current_user, get_current_active_superuser

# Models - ĐỔI TÊN ĐỂ TRÁNH CONFLICT
from app.models.user import User as UserModel  # ← User model (database)

# Router
router = APIRouter(prefix="/users", tags=["User Management"])


@router.get("/", response_model=PaginatedResponse[User])
def get_users(
    page: int = Query(default=1, ge=1, description="Số trang"),
    page_size: int = Query(default=10, ge=1, le=100, description="Số items mỗi trang"),
    search: Optional[str] = Query(
        default=None, description="Tìm kiếm theo username, email, full_name"
    ),
    is_active: Optional[bool] = Query(
        default=None, description="Lọc theo trạng thái active"
    ),
    is_superuser: Optional[bool] = Query(
        default=None, description="Lọc theo superuser"
    ),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    ## Lấy danh sách users (có phân trang)

    **Yêu cầu:** User đã đăng nhập

    **Chức năng:**
    - Phân trang kết quả
    - Tìm kiếm theo username, email, hoặc full_name
    - Lọc theo trạng thái active/inactive
    - Lọc theo quyền superuser

    **Response:**
    - `200 OK`: Trả về danh sách users với pagination metadata
    - `401 Unauthorized`: Chưa đăng nhập hoặc token không hợp lệ

    **Ví dụ:**
    ```
    GET /api/v1/users/?page=1&page_size=10&search=admin
    ```
    """
    skip = (page - 1) * page_size

    users, total = UserService.get_users(
        db=db,
        skip=skip,
        limit=page_size,
        search=search,
        is_active=is_active,
        is_superuser=is_superuser,
    )

    return PaginatedResponse.create(
        items=users, total=total, page=page, page_size=page_size
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """
    ## Xóa user (Soft Delete)

    **Yêu cầu:** Chỉ Superuser/Admin

    **Chức năng:**
    - Đặt user thành inactive (soft delete)
    - Không xóa vật lý khỏi database
    - Không thể tự xóa chính mình

    **Response:**
    - `204 No Content`: Xóa thành công
    - `400 Bad Request`: Cố gắng xóa chính mình
    - `403 Forbidden`: Không phải superuser
    - `404 Not Found`: User không tồn tại
    - `401 Unauthorized`: Chưa đăng nhập

    **Lưu ý:** Để khôi phục user, dùng endpoint PATCH /users/{user_id}/activate
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không thể xóa chính mình. Vui lòng sử dụng tài khoản admin khác.",
        )

    success = UserService.delete_user(db, user_id=user_id)

    if not success:
        raise ResourceNotFoundError("User", user_id)

    return None
