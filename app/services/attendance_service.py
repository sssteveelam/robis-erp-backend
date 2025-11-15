"""
Attendance Service với auto-calculate
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, time, datetime, timedelta

from app.models.attendance import Attendance
from app.models.hr import Employee
from app.schemas.attendance import (
    AttendanceCheckIn,
    AttendanceCheckOut,
    AttendanceLeaveRequest,
    AttendanceReport,
)


class AttendanceService:

    # Cấu hình giờ làm việc
    WORK_START_TIME = time(9, 0)  # 9:00 AM
    WORK_END_TIME = time(17, 0)  # 5:00 PM
    WORK_HOURS_PER_DAY = 8

    @staticmethod
    def calculate_late_minutes(check_in: time) -> int:
        """Tính số phút đi muộn"""
        if check_in <= AttendanceService.WORK_START_TIME:
            return 0

        start_minutes = (
            AttendanceService.WORK_START_TIME.hour * 60
            + AttendanceService.WORK_START_TIME.minute
        )
        checkin_minutes = check_in.hour * 60 + check_in.minute

        return checkin_minutes - start_minutes

    @staticmethod
    def calculate_overtime_minutes(check_out: time) -> int:
        """Tính số phút làm thêm"""
        if check_out <= AttendanceService.WORK_END_TIME:
            return 0

        end_minutes = (
            AttendanceService.WORK_END_TIME.hour * 60
            + AttendanceService.WORK_END_TIME.minute
        )
        checkout_minutes = check_out.hour * 60 + check_out.minute

        return checkout_minutes - end_minutes

    @staticmethod
    def calculate_work_hours(check_in: time, check_out: time) -> int:
        """Tính tổng giờ làm việc (phút)"""
        if not check_in or not check_out:
            return 0

        checkin_minutes = check_in.hour * 60 + check_in.minute
        checkout_minutes = check_out.hour * 60 + check_out.minute

        # Trừ 1 tiếng nghỉ trưa (12:00-13:00)
        work_minutes = checkout_minutes - checkin_minutes - 60

        return max(0, work_minutes)

    @staticmethod
    def check_in(db: Session, check_in_data: AttendanceCheckIn) -> Attendance:
        """Chấm công vào"""
        today = date.today()

        # Kiểm tra đã check-in chưa
        existing = (
            db.query(Attendance)
            .filter(
                Attendance.employee_id == check_in_data.employee_id,
                Attendance.date == today,
            )
            .first()
        )

        if existing:
            raise ValueError("Employee đã check-in hôm nay rồi!")

        # Tính late minutes
        late_minutes = AttendanceService.calculate_late_minutes(check_in_data.check_in)

        # Determine status
        status = "late" if late_minutes > 0 else "present"

        # Create attendance record
        attendance = Attendance(
            employee_id=check_in_data.employee_id,
            date=today,
            check_in=check_in_data.check_in,
            late_minutes=late_minutes,
            status=status,
            note=check_in_data.note,
        )

        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        return attendance

    @staticmethod
    def check_out(
        db: Session, check_out_data: AttendanceCheckOut
    ) -> Optional[Attendance]:
        """Chấm công ra"""
        today = date.today()

        # Tìm attendance record
        attendance = (
            db.query(Attendance)
            .filter(
                Attendance.employee_id == check_out_data.employee_id,
                Attendance.date == today,
            )
            .first()
        )

        if not attendance:
            raise ValueError("Employee chưa check-in hôm nay!")

        if attendance.check_out:
            raise ValueError("Employee đã check-out rồi!")

        # Update check-out
        attendance.check_out = check_out_data.check_out

        # Tính overtime & work hours
        attendance.overtime_minutes = AttendanceService.calculate_overtime_minutes(
            check_out_data.check_out
        )
        attendance.work_hours = AttendanceService.calculate_work_hours(
            attendance.check_in, attendance.check_out
        )

        if check_out_data.note:
            attendance.note = (attendance.note or "") + " | " + check_out_data.note

        db.commit()
        db.refresh(attendance)
        return attendance

    @staticmethod
    def request_leave(
        db: Session,
        leave_request: AttendanceLeaveRequest,
        approved_by: Optional[int] = None,
    ) -> Attendance:
        """Đăng ký nghỉ phép"""

        # Kiểm tra đã có record chưa
        existing = (
            db.query(Attendance)
            .filter(
                Attendance.employee_id == leave_request.employee_id,
                Attendance.date == leave_request.date,
            )
            .first()
        )

        if existing:
            raise ValueError("Đã có attendance record cho ngày này!")

        # Create leave record
        attendance = Attendance(
            employee_id=leave_request.employee_id,
            date=leave_request.date,
            status="leave",
            leave_type=leave_request.leave_type,
            note=leave_request.note,
            approved_by=approved_by,
            approved_at=datetime.utcnow() if approved_by else None,
        )

        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        return attendance

    @staticmethod
    def get_attendance_records(
        db: Session,
        employee_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Attendance], int]:
        """Lấy danh sách attendance records"""
        query = db.query(Attendance)

        if employee_id:
            query = query.filter(Attendance.employee_id == employee_id)
        if start_date:
            query = query.filter(Attendance.date >= start_date)
        if end_date:
            query = query.filter(Attendance.date <= end_date)

        total = query.count()
        records = query.order_by(Attendance.date.desc()).offset(skip).limit(limit).all()

        return records, total

    @staticmethod
    def get_monthly_report(
        db: Session, employee_id: int, month: str
    ) -> AttendanceReport:
        """
        Báo cáo chấm công tháng
        month format: "2025-11"
        """
        year, month_num = month.split("-")
        start_date = date(int(year), int(month_num), 1)

        # End date = last day of month
        if int(month_num) == 12:
            end_date = date(int(year) + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(int(year), int(month_num) + 1, 1) - timedelta(days=1)

        # Get records
        records = (
            db.query(Attendance)
            .filter(
                Attendance.employee_id == employee_id,
                Attendance.date >= start_date,
                Attendance.date <= end_date,
            )
            .all()
        )

        # Calculate summary
        total_days = len(records)
        present_days = len([r for r in records if r.status == "present"])
        late_days = len([r for r in records if r.status == "late"])
        absent_days = len([r for r in records if r.status == "absent"])
        leave_days = len([r for r in records if r.status in ["leave", "sick_leave"]])

        total_late_minutes = sum(r.late_minutes for r in records)
        total_overtime_minutes = sum(r.overtime_minutes for r in records)
        total_work_hours = sum(r.work_hours for r in records)

        # Get employee name
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        employee_name = employee.full_name if employee else "Unknown"

        return AttendanceReport(
            employee_id=employee_id,
            employee_name=employee_name,
            month=month,
            total_days=total_days,
            present_days=present_days,
            late_days=late_days,
            absent_days=absent_days,
            leave_days=leave_days,
            total_late_minutes=total_late_minutes,
            total_overtime_minutes=total_overtime_minutes,
            total_work_hours=total_work_hours,
        )
