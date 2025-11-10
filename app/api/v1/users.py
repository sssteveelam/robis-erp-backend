from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.db.database import get_db
from app.schemas.user import User, UserUpdate
from app.schemas.common import PaginatedResponse, PaginationParams
from app.services.user_service import UserService
from app.api.dependencies.auth import get_current_user, get_current_active_superuser
from app.models.user import User as UserModel

router = APIRouter(prefix="/users", tags=["User Management"])


@router.get("/", response_model=PaginatedResponse[User])
def get_users(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(
        default=None, description="Search by username, email, or full name"
    ),
    is_active: Optional[bool] = Query(
        default=None, description="Filter by active status"
    ),
    is_superuser: Optional[bool] = Query(
        default=None, description="Filter by superuser status"
    ),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    **Lấy danh sách users (có pagination và filtering)**

    - Chỉ authenticated users mới được truy cập
    - Hỗ trợ search, filter, pagination

    Query Parameters:
    - **page**: Trang số (bắt đầu từ 1)
    - **page_size**: Số items mỗi trang (tối đa 100)
    - **search**: Tìm kiếm theo username, email, hoặc full name
    - **is_active**: Filter theo trạng thái active (true/false)
    - **is_superuser**: Filter theo superuser (true/false)
    """
    # Calculate skip
    skip = (page - 1) * page_size

    # Get users with filters
    users, total = UserService.get_users(
        db=db,
        skip=skip,
        limit=page_size,
        search=search,
        is_active=is_active,
        is_superuser=is_superuser,
    )

    # Create paginated response
    return PaginatedResponse.create(
        items=users, total=total, page=page, page_size=page_size
    )


@router.get("/{user_id}", response_model=User)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    **Lấy thông tin chi tiết của 1 user**

    - Chỉ authenticated users mới được truy cập
    - Trả về 404 nếu user không tồn tại
    """
    user = UserService.get_user(db, user_id=user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    return user


@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    **Update thông tin user**

    - User chỉ có thể update chính mình
    - Superuser có thể update bất kỳ user nào
    - Chỉ update các fields được gửi lên (partial update)
    """
    # Check permission: Chỉ cho phép update chính mình hoặc là superuser
    if user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. You can only update your own profile.",
        )

    updated_user = UserService.update_user(db, user_id=user_id, user_update=user_update)

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """
    **Xóa user (soft delete)**

    - Chỉ superuser mới được xóa user
    - Soft delete: Set is_active = False
    - Không cho phép xóa chính mình
    """
    # Không cho phép superuser tự xóa chính mình
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself"
        )

    success = UserService.delete_user(db, user_id=user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    return None


@router.patch("/{user_id}/activate", response_model=User)
def activate_user(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """
    **Kích hoạt hoặc vô hiệu hóa user**

    - Chỉ superuser mới được thực hiện
    - is_active=true: Kích hoạt user
    - is_active=false: Vô hiệu hóa user (không cho login)
    """
    user = UserService.activate_user(db, user_id=user_id, is_active=is_active)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    return user


@router.patch("/{user_id}/superuser", response_model=User)
def set_superuser(
    user_id: int,
    is_superuser: bool,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """
    **Đặt hoặc bỏ quyền superuser**

    - Chỉ superuser hiện tại mới được thực hiện
    - is_superuser=true: Đặt user thành superuser
    - is_superuser=false: Bỏ quyền superuser
    - Không cho phép tự bỏ quyền superuser của chính mình
    """
    # Không cho phép superuser tự bỏ quyền của chính mình
    if user_id == current_user.id and not is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove your own superuser privilege",
        )

    user = UserService.set_superuser(db, user_id=user_id, is_superuser=is_superuser)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found",
        )

    return user
