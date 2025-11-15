"""
Attendance Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time, datetime
from enum import Enum


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    LATE = "late"
    ABSENT = "absent"
    LEAVE = "leave"
    SICK_LEAVE = "sick_leave"


class LeaveType(str, Enum):
    ANNUAL = "annual"
    SICK = "sick"
    PERSONAL = "personal"
    MATERNITY = "maternity"
    UNPAID = "unpaid"


# ============= ATTENDANCE SCHEMAS =============


class AttendanceBase(BaseModel):
    employee_id: int
    date: date
    status: AttendanceStatus = AttendanceStatus.PRESENT


class AttendanceCheckIn(BaseModel):
    """Schema cho check-in"""

    employee_id: int
    check_in: time
    note: Optional[str] = Field(None, max_length=500)


class AttendanceCheckOut(BaseModel):
    """Schema cho check-out"""

    employee_id: int
    check_out: time
    note: Optional[str] = Field(None, max_length=500)


class AttendanceLeaveRequest(BaseModel):
    """Schema cho nghỉ phép"""

    employee_id: int
    date: date
    leave_type: LeaveType
    note: Optional[str] = Field(None, max_length=500)


class Attendance(AttendanceBase):
    id: int
    check_in: Optional[time] = None
    check_out: Optional[time] = None
    late_minutes: int = 0
    overtime_minutes: int = 0
    work_hours: int = 0
    leave_type: Optional[LeaveType] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    note: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AttendanceReport(BaseModel):
    """Báo cáo chấm công tháng"""

    employee_id: int
    employee_name: str
    month: str  # "2025-11"
    total_days: int
    present_days: int
    late_days: int
    absent_days: int
    leave_days: int
    total_late_minutes: int
    total_overtime_minutes: int
    total_work_hours: int
