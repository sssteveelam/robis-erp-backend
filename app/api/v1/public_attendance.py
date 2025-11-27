"""
Public Attendance API Endpoints (QR/Kiosk)

Các endpoints này cho phép chấm công nhanh mà không cần đăng nhập user.
Bảo mật bằng service token (ATTEND_PUBLIC_TOKEN).

Endpoints:
- GET /api/v1/public/employees - Lấy danh sách nhân viên
- POST /api/v1/public/attendance/check-in - Chấm công vào
- POST /api/v1/public/attendance/check-out - Chấm công ra
- POST /api/v1/public/attendance/leave - Đăng ký nghỉ phép
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, time

from app.db.database import get_db
from app.schemas.attendance import (
    Attendance,
    AttendanceCheckIn,
    AttendanceCheckOut,
    LeaveType,
)
from app.schemas.hr import Employee, PublicEmployee
from app.schemas.common import PaginatedResponse
from app.services.attendance_service import AttendanceService
from app.services.hr_service import EmployeeService
from app.api.dependencies.service_auth import service_token_auth
from app.core.config import settings

router = APIRouter(prefix="/api/v1/public", tags=["Public Attendance (QR/Kiosk)"])


def _ensure_public_auth(request: Request) -> bool:
    """
    Bảo vệ endpoints attendance (check-in/out/leave).

    - Nếu PUBLIC_ATTEND_ACTIONS_OPEN=False => bắt buộc service token
    - Nếu PUBLIC_ATTEND_ACTIONS_OPEN=True => cho phép:
        + Có service token hợp lệ HOẶC
        + Kiosk secret và/hoặc IP trong whitelist
    """
    # 1) Nếu chưa mở public actions -> yêu cầu token
    if not settings.PUBLIC_ATTEND_ACTIONS_OPEN:
        return service_token_auth(request)

    # 2) Nếu đã mở, ưu tiên cho phép nếu có token hợp lệ
    try:
        return service_token_auth(request)
    except Exception:
        pass  # Không có/không đúng token, chuyển sang kiểm tra kiosk

    # 3) Kiểm tra kiosk secret (nếu cấu hình)
    kiosk_secret_cfg = (settings.PUBLIC_KIOSK_DEVICE_SECRET or "").strip()
    if kiosk_secret_cfg:
        kiosk_secret = (request.headers.get("X-Kiosk-Secret", "") or "").strip()
        if kiosk_secret != kiosk_secret_cfg:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated (kiosk)")

    # 4) Kiểm tra whitelist IP (nếu cấu hình)
    ip_csv = (settings.PUBLIC_KIOSK_IP_WHITELIST or "").strip()
    if ip_csv:
        allowed = {ip.strip() for ip in ip_csv.split(",") if ip.strip()}
        req_ip = request.client.host if request and request.client else None
        if allowed and req_ip not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden from this IP")

    return True


# ============= PUBLIC EMPLOYEE ENDPOINTS =============


@router.get(
    "/employees",
    response_model=PaginatedResponse[PublicEmployee],
)
def public_get_employees(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: Optional[str] = Query(
        default=None, description="Tìm theo name, email, employee_code"
    ),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Lấy danh sách nhân viên để chọn từ QR kiosk

    Chỉ trả về các fields công khai (id, employee_code, full_name, department_id).
    Không trả về thông tin nhạy cảm (salary, personal info).

    **Authentication**:
    - Mặc định: Service token (ATTEND_PUBLIC_TOKEN) trong Authorization header
    - Nếu bật PUBLIC_EMPLOYEES_OPEN: không cần token, nhưng bắt buộc search tối thiểu và giới hạn page_size
    """
    # Auth/toggle logic for employees list
    if not settings.PUBLIC_EMPLOYEES_OPEN:
        # Require service token
        service_token_auth(request)
    else:
        # Enforce search minimum length
        if not search or len(search.strip()) < settings.PUBLIC_EMPLOYEES_MIN_SEARCH_LEN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Vui lòng nhập từ khóa tối thiểu {settings.PUBLIC_EMPLOYEES_MIN_SEARCH_LEN} ký tự",
            )
        # Cap page_size when open
        page_size = min(page_size, settings.PUBLIC_EMPLOYEES_MAX_PAGE_SIZE)

    skip = (page - 1) * page_size

    # Gọi service hiện có
    employees, total = EmployeeService.get_employees(
        db=db,
        skip=skip,
        limit=page_size,
        search=search,
        employment_status="active",  # Chỉ lấy nhân viên đang hoạt động
    )

    # Rút gọn fields để tránh lộ thông tin nhạy cảm
    # Chỉ trả về: id, employee_code, full_name
    slim_employees = [
        PublicEmployee(
            id=emp.id,
            employee_code=emp.employee_code,
            full_name=emp.full_name,
        )
        for emp in employees
    ]

    return PaginatedResponse.create(
        items=slim_employees, total=total, page=page, page_size=page_size
    )


# ============= PUBLIC ATTENDANCE ENDPOINTS =============


@router.post(
    "/attendance/check-in",
    response_model=Attendance,
    status_code=status.HTTP_201_CREATED,
)
def public_check_in(
    payload: AttendanceCheckIn,
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Chấm công vào (QR/Kiosk)

    Auto-calculate late_minutes nếu check_in > 9:00

    **Request body**:
    - employee_id: ID nhân viên
    - check_in: Giờ chấm công (HH:MM:SS)
    - note: Ghi chú (tùy chọn)

    **Authentication**:
    - Mặc định: Service token (ATTEND_PUBLIC_TOKEN) trong Authorization header
    - Nếu bật PUBLIC_ATTEND_ACTIONS_OPEN: chấp nhận token HOẶC header X-Kiosk-Secret hợp lệ và/hoặc IP whitelist
    """
    try:
        _ensure_public_auth(request)
        return AttendanceService.check_in(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/attendance/check-out",
    response_model=Attendance,
    status_code=status.HTTP_200_OK,
)
def public_check_out(
    payload: AttendanceCheckOut,
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Chấm công ra (QR/Kiosk)

    Auto-calculate overtime_minutes và work_hours

    **Request body**:
    - employee_id: ID nhân viên
    - check_out: Giờ chấm công (HH:MM:SS)
    - note: Ghi chú (tùy chọn)

    **Authentication**:
    - Mặc định: Service token (ATTEND_PUBLIC_TOKEN) trong Authorization header
    - Nếu bật PUBLIC_ATTEND_ACTIONS_OPEN: chấp nhận token HOẶC header X-Kiosk-Secret hợp lệ và/hoặc IP whitelist
    """
    try:
        _ensure_public_auth(request)
        return AttendanceService.check_out(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/attendance/leave",
    response_model=Attendance,
    status_code=status.HTTP_201_CREATED,
)
def public_request_leave(
    payload: dict,  # Flexible payload
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Đăng ký nghỉ phép (QR/Kiosk)

    **Request body**:
    - employee_id: ID nhân viên
    - leave_type: Loại nghỉ (annual, sick, personal, maternity, unpaid)
    - start_date: Ngày bắt đầu (YYYY-MM-DD)
    - end_date: Ngày kết thúc (YYYY-MM-DD)
    - reason: Lý do (tùy chọn)
    - note: Ghi chú (tùy chọn)

    **Authentication**: Service token (ATTEND_PUBLIC_TOKEN) via Authorization header

    **Example**:
    ```json
    {
      "employee_id": 123,
      "leave_type": "personal",
      "start_date": "2025-11-27",
      "end_date": "2025-11-27",
      "reason": "Việc riêng"
    }
    ```
    """
    try:
        _ensure_public_auth(request)
        # Validate required fields
        required_fields = ["employee_id", "leave_type", "start_date", "end_date"]
        for field in required_fields:
            if field not in payload:
                raise ValueError(f"Missing required field: {field}")

        employee_id = payload.get("employee_id")
        leave_type = payload.get("leave_type")
        start_date_str = payload.get("start_date")
        end_date_str = payload.get("end_date")
        reason = payload.get("reason")
        note = payload.get("note")

        # Parse dates
        try:
            start_date = date.fromisoformat(start_date_str)
            end_date = date.fromisoformat(end_date_str)
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")

        # Validate leave_type
        valid_leave_types = ["annual", "sick", "personal", "maternity", "unpaid"]
        if leave_type not in valid_leave_types:
            raise ValueError(f"Invalid leave_type. Must be one of: {valid_leave_types}")

        # Process each day in the range
        current_date = start_date
        results = []

        while current_date <= end_date:
            # Create leave request for this day
            from app.schemas.attendance import AttendanceLeaveRequest

            leave_req = AttendanceLeaveRequest(
                employee_id=employee_id,
                date=current_date,
                leave_type=leave_type,
                note=note or reason,
            )

            try:
                result = AttendanceService.request_leave(db, leave_req)
                results.append(result)
            except ValueError as e:
                # Nếu ngày này đã có record, bỏ qua
                pass

            # Move to next day
            from datetime import timedelta

            current_date += timedelta(days=1)

        if not results:
            raise ValueError("No leave records created (all dates may already exist)")

        # Return first result (hoặc có thể return list)
        return results[0]

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

