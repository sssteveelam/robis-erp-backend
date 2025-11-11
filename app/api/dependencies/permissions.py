from fastapi import Depends, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.api.dependencies.auth import get_current_user
from app.core.exceptions import PermissionDeniedError


def require_permission(permission_name: str):
    """
    Dependency: Kiểm tra user có permission cụ thể không

    Args:
        permission_name: Tên permission cần kiểm tra (VD: "orders:create")

    Returns:
        Dependency function

    Raises:
        PermissionDeniedError: Nếu user không có quyền

    Examples:
        >>> @router.post("/orders", dependencies=[Depends(require_permission("orders:create"))])
        >>> def create_order():
        >>>     return {"message": "Order created"}
    """

    def permission_checker(
        db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
    ):
        # Superuser có mọi quyền
        if current_user.is_superuser:
            return

        # Collect tất cả permissions từ các roles của user
        user_permissions = set()
        for role in current_user.roles:
            if role.is_active:  # Chỉ check role đang active
                user_permissions.update(perm.name for perm in role.permissions)

        # Kiểm tra permission
        if permission_name not in user_permissions:
            raise PermissionDeniedError(
                permission_name=permission_name,
                detail=f"Bạn không có quyền '{permission_name}'. "
                f"Quyền hiện tại: {', '.join(sorted(user_permissions)) or 'Không có quyền nào'}. "
                f"Vui lòng liên hệ quản trị viên để được cấp quyền.",
            )

        return True

    return Depends(permission_checker)
