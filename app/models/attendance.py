"""
Attendance Model - Chấm công
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Date,
    Time,
    DateTime,
    Text,
    Numeric,
    Boolean,
    Enum,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class AttendanceStatus(str, enum.Enum):
    """Trạng thái chấm công"""

    PRESENT = "present"  # Có mặt
    LATE = "late"  # Đi muộn
    ABSENT = "absent"  # Vắng mặt
    LEAVE = "leave"  # Nghỉ phép (có phép)
    SICK_LEAVE = "sick_leave"  # Nghỉ bệnh


class LeaveType(str, enum.Enum):
    """Loại nghỉ phép"""

    ANNUAL = "annual"  # Nghỉ phép năm
    SICK = "sick"  # Nghỉ bệnh
    PERSONAL = "personal"  # Nghỉ cá nhân
    MATERNITY = "maternity"  # Nghỉ thai sản
    UNPAID = "unpaid"  # Nghỉ không lương


class Attendance(Base):
    """Chấm công"""

    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)

    # Employee & Date
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)

    # Check-in/out
    check_in = Column(Time)  # Giờ vào
    check_out = Column(Time)  # Giờ ra

    # Auto-calculated fields
    late_minutes = Column(Integer, default=0)  # Số phút đi muộn (nếu check_in > 9:00)
    overtime_minutes = Column(
        Integer, default=0
    )  # Số phút làm thêm (nếu check_out > 17:00)
    work_hours = Column(Integer, default=0)  # Tổng giờ làm việc (phút)

    # Status & Leave
    status = Column(
        Enum(AttendanceStatus), default=AttendanceStatus.PRESENT, nullable=False
    )
    leave_type = Column(Enum(LeaveType))  # Nếu status = LEAVE

    # Approval (cho nghỉ phép)
    approved_by = Column(Integer, ForeignKey("employees.id"))  # Manager approve
    approved_at = Column(DateTime)

    # Notes
    note = Column(String(500))

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    employee = relationship(
        "Employee", foreign_keys=[employee_id], back_populates="attendance_records"
    )
    approved_by_manager = relationship("Employee", foreign_keys=[approved_by])

    # Unique constraint: 1 employee chỉ có 1 record/ngày
    __table_args__ = ({"schema": None, "extend_existing": True},)


