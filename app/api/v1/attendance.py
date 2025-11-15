"""
Attendance API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.db.database import get_db
from app.schemas.attendance import (
    Attendance,
    AttendanceCheckIn,
    AttendanceCheckOut,
    AttendanceLeaveRequest,
    AttendanceReport,
)
from app.schemas.common import PaginatedResponse
from app.services.attendance_service import AttendanceService
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.models.user import User as UserModel

router = APIRouter(tags=["Attendance"])


@router.post(
    "/attendance/check-in",
    response_model=Attendance,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission("hr:read")],
)
def check_in(
    check_in_data: AttendanceCheckIn,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Chấm công vào

    Auto-calculate late_minutes nếu check_in > 9:00
    """
    try:
        return AttendanceService.check_in(db, check_in_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/attendance/check-out",
    response_model=Attendance,
    dependencies=[require_permission("hr:read")],
)
def check_out(
    check_out_data: AttendanceCheckOut,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Chấm công ra

    Auto-calculate overtime_minutes và work_hours
    """
    try:
        return AttendanceService.check_out(db, check_out_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/attendance/leave",
    response_model=Attendance,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission("hr:read")],
)
def request_leave(
    leave_request: AttendanceLeaveRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Đăng ký nghỉ phép

    Leave types: annual, sick, personal, maternity, unpaid
    """
    try:
        # TODO: approved_by = manager_id (lấy từ employee.direct_manager_id)
        return AttendanceService.request_leave(db, leave_request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/attendance",
    response_model=PaginatedResponse[Attendance],
    dependencies=[require_permission("hr:read")],
)
def get_attendance_records(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    employee_id: Optional[int] = Query(default=None),
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Lấy danh sách attendance records"""
    skip = (page - 1) * page_size

    records, total = AttendanceService.get_attendance_records(
        db=db,
        skip=skip,
        limit=page_size,
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
    )

    return PaginatedResponse.create(
        items=records, total=total, page=page, page_size=page_size
    )


@router.get(
    "/attendance/report/monthly/{employee_id}",
    response_model=AttendanceReport,
    dependencies=[require_permission("hr:read")],
)
def get_monthly_report(
    employee_id: int,
    month: str = Query(..., description="Format: YYYY-MM, VD: 2025-11"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Báo cáo chấm công tháng

    Trả về tổng hợp: present_days, late_days, absent_days, total_work_hours...
    """
    return AttendanceService.get_monthly_report(db, employee_id, month)
