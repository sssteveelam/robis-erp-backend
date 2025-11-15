"""
HR Models - Departments, Positions, Employees
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Date,
    DateTime,
    Text,
    Numeric,
    Enum,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class DepartmentType(str, enum.Enum):
    """3 loại bộ phận theo Robis"""

    OPERATION = "operation"  # Sản xuất: QC, Warehouse, Production
    COMMERCIAL = "commercial"  # Kinh doanh: Sales, Marketing
    SUPPORT = "support"  # Hỗ trợ: HR, IT, Accounting


class Department(Base):
    """Bộ phận"""

    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    type = Column(Enum(DepartmentType), nullable=False)
    budget = Column(Numeric(15, 2))  # Ngân sách hàng năm
    manager_id = Column(Integer, ForeignKey("employees.id"))  # Trưởng bộ phận
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    positions = relationship("Position", back_populates="department")
    employees = relationship(
        "Employee", foreign_keys="Employee.department_id", back_populates="department"
    )
    manager = relationship(
        "Employee",
        foreign_keys=[manager_id],
        remote_side="Employee.id",
        post_update=True,
    )


class Position(Base):
    """Chức vụ với level system 1-5"""

    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), unique=True, nullable=False)
    level = Column(
        Integer, nullable=False
    )  # 1=Entry, 2=Junior, 3=Senior, 4=Lead, 5=Manager
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    department = relationship("Department", back_populates="positions")
    employees = relationship("Employee", back_populates="position")


class EmploymentStatus(str, enum.Enum):
    """Trạng thái nhân viên"""

    ACTIVE = "active"  # Đang làm việc
    PROBATION = "probation"  # Thử việc
    TERMINATED = "terminated"  # Đã nghỉ việc
    ON_LEAVE = "on_leave"  # Nghỉ phép dài hạn


class Employee(Base):
    """Nhân viên"""

    __tablename__ = "employees"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Basic Info
    employee_code = Column(String(20), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))

    # Department & Position
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    position_id = Column(Integer, ForeignKey("positions.id"), nullable=False)

    # Management Structure
    direct_manager_id = Column(Integer, ForeignKey("employees.id"))
    hr_contact_id = Column(Integer, ForeignKey("employees.id"))

    # Employment Info
    hire_date = Column(Date, nullable=False)
    employment_status = Column(
        Enum(EmploymentStatus), default=EmploymentStatus.ACTIVE, nullable=False
    )
    salary_range = Column(String(50))

    # User Link
    user_id = Column(Integer, ForeignKey("users.id"))

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    department = relationship(
        "Department", foreign_keys=[department_id], back_populates="employees"
    )
    position = relationship("Position", back_populates="employees")

    # Self-referencing
    direct_manager = relationship(
        "Employee",
        foreign_keys=[direct_manager_id],
        remote_side=[id],
        backref="subordinates",
    )
    hr_contact = relationship(
        "Employee", foreign_keys=[hr_contact_id], remote_side=[id]
    )

    # User
    user = relationship("User", foreign_keys=[user_id])

    # Attendance & Performance - FIX AMBIGUOUS FOREIGN KEYS
    attendance_records = relationship(
        "Attendance", foreign_keys="Attendance.employee_id", back_populates="employee"
    )
    performance_reviews_received = relationship(
        "PerformanceReview",
        foreign_keys="PerformanceReview.employee_id",
        back_populates="employee",
    )
    performance_reviews_given = relationship(
        "PerformanceReview",
        foreign_keys="PerformanceReview.reviewer_id",
        back_populates="reviewer",
    )
