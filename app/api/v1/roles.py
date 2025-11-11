from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.db.database import get_db
from app.schemas.role import (
    Role,
    RoleCreate,
    RoleUpdate,
    RoleWithPermissions,
    Permission,
    PermissionAssignment,
)
from app.schemas.common import PaginatedResponse
from app.services.role_service import RoleService, PermissionService
from app.api.dependencies.auth import get_current_active_superuser
from app.models.user import User as UserModel

router = APIRouter(prefix="/roles", tags=["Role Management"])


@router.post(
    "/",
    response_model=Role,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Role được tạo thành công"},
        400: {"description": "Dữ liệu không hợp lệ (VD: tên role đã tồn tại)"},
        401: {"description": "Chưa đăng nhập"},
        403: {"description": "Không có quyền (chỉ superuser)"},
    },
)
def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """
    ## Tạo role mới trong hệ thống

    **Yêu cầu:** Chỉ Superuser/Admin

    **Request Body:**
    ```
    {
      "name": "QC_STAFF",
      "description": "Nhân viên kiểm tra chất lượng",
      "is_active": true
    }
    ```

    **Quy tắc:**
    - Tên role phải unique
    - Tên nên viết IN HOA, không dấu, dùng underscore (VD: QC_STAFF, SALES_REP)
    - Description nên mô tả rõ vai trò

    **Response:**
    - `201 Created`: Role được tạo thành công
    - `400 Bad Request`: Tên role đã tồn tại
    - `403 Forbidden`: Không phải superuser
    """
    existing_role = RoleService.get_role_by_name(db, name=role.name)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role với tên '{role.name}' đã tồn tại. Vui lòng chọn tên khác.",
        )

    return RoleService.create_role(db, role=role)
