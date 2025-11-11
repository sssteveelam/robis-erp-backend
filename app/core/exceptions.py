"""
Custom Exception Classes và Error Response Models
"""

from fastapi import HTTPException, status
from typing import Optional


class PermissionDeniedError(HTTPException):

    def __init__(self, permission_name: str, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
            or f"Bạn không có quyền: {permission_name}. Vui lòng liên hệ quản trị viên để được cấp quyền.",
        )


class UnauthorizedError(HTTPException):

    def __init__(self, detail: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
            or "Bạn chưa đăng nhập hoặc phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.",
            headers={"WWW-Authenticate": "Bearer"},
        )


class InactiveUserError(HTTPException):

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản của bạn đã bị vô hiệu hóa. Vui lòng liên hệ quản trị viên.",
        )


class ResourceNotFoundError(HTTPException):

    def __init__(self, resource_type: str, resource_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_type} với ID {resource_id} không tồn tại.",
        )
