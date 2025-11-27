"""
Service Token Authentication for Public QR/Kiosk Endpoints

Cho phép truy cập các public endpoints (chấm công nhanh) mà không cần JWT user.
Bảo mật bằng 1 service token riêng (ATTEND_PUBLIC_TOKEN) gắn trong header Authorization.
"""

import os
from fastapi import Depends, HTTPException, status, Request

SERVICE_TOKEN = os.getenv("ATTEND_PUBLIC_TOKEN", "").strip()


def service_token_auth(request: Request) -> bool:
    """
    Dependency: Xác thực service token cho public endpoints

    Chấp nhận:
    - Header Authorization: Bearer <ATTEND_PUBLIC_TOKEN>
    - Hoặc Authorization: <ATTEND_PUBLIC_TOKEN>

    Raises:
        HTTPException 500: Service token chưa được cấu hình
        HTTPException 401: Token không hợp lệ hoặc không khớp
    """
    if not SERVICE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service token not configured on server",
        )

    # Lấy Authorization header
    auth = request.headers.get("Authorization", "")

    # Parse token: chấp nhận "Bearer <token>" hoặc raw "<token>"
    if auth.startswith("Bearer "):
        token = auth[len("Bearer ") :].strip()
    else:
        token = auth.strip()

    # Kiểm tra token
    if not token or token != SERVICE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing service token",
        )

    return True

