"""
HR Service - Department, Position, Employee
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime

from app.models.hr import Department, Position, Employee
from app.schemas.hr import (
    DepartmentCreate,
    DepartmentUpdate,
    PositionCreate,
    PositionUpdate,
    EmployeeCreate,
    EmployeeUpdate,
)


# ============= DEPARTMENT SERVICE =============


class DepartmentService:

    @staticmethod
    def create_department(db: Session, department: DepartmentCreate) -> Department:
        """Tạo department mới"""
        db_department = Department(**department.dict())
        db.add(db_department)
        db.commit()
        db.refresh(db_department)
        return db_department

    @staticmethod
    def get_departments(
        db: Session, skip: int = 0, limit: int = 100, type: Optional[str] = None
    ) -> tuple[List[Department], int]:
        """Lấy danh sách departments"""
        query = db.query(Department)

        if type:
            query = query.filter(Department.type == type)

        total = query.count()
        departments = query.offset(skip).limit(limit).all()

        return departments, total

    @staticmethod
    def get_department_by_id(db: Session, department_id: int) -> Optional[Department]:
        """Lấy department theo ID"""
        return db.query(Department).filter(Department.id == department_id).first()

    @staticmethod
    def update_department(
        db: Session, department_id: int, department_update: DepartmentUpdate
    ) -> Optional[Department]:
        """Cập nhật department"""
        db_department = (
            db.query(Department).filter(Department.id == department_id).first()
        )

        if not db_department:
            return None

        update_data = department_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_department, key, value)

        db.commit()
        db.refresh(db_department)
        return db_department


# ============= POSITION SERVICE =============


class PositionService:

    @staticmethod
    def create_position(db: Session, position: PositionCreate) -> Position:
        """Tạo position mới"""
        db_position = Position(**position.dict())
        db.add(db_position)
        db.commit()
        db.refresh(db_position)
        return db_position

    @staticmethod
    def get_positions(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        department_id: Optional[int] = None,
        level: Optional[int] = None,
    ) -> tuple[List[Position], int]:
        """Lấy danh sách positions"""
        query = db.query(Position)

        if department_id:
            query = query.filter(Position.department_id == department_id)
        if level:
            query = query.filter(Position.level == level)

        total = query.count()
        positions = query.offset(skip).limit(limit).all()

        return positions, total

    @staticmethod
    def get_position_by_id(db: Session, position_id: int) -> Optional[Position]:
        """Lấy position theo ID"""
        return db.query(Position).filter(Position.id == position_id).first()

    @staticmethod
    def get_career_path(db: Session, position_id: int) -> List[Position]:
        """Lấy lộ trình thăng tiến (career path)"""
        position = db.query(Position).filter(Position.id == position_id).first()

        if not position:
            return []

        # Lấy các positions trong cùng department với level cao hơn
        next_positions = (
            db.query(Position)
            .filter(
                Position.department_id == position.department_id,
                Position.level > position.level,
            )
            .order_by(Position.level)
            .all()
        )

        return next_positions


# ============= EMPLOYEE SERVICE =============


class EmployeeService:

    @staticmethod
    def generate_employee_code(db: Session) -> str:
        """
        Auto-generate employee code: EMP0001, EMP0002, ...
        """
        # Lấy employee code lớn nhất
        max_code = db.query(func.max(Employee.employee_code)).scalar()

        if not max_code:
            return "EMP0001"

        # Extract số từ code (EMP0001 → 1)
        current_number = int(max_code.replace("EMP", ""))
        next_number = current_number + 1

        # Format: EMP0001, EMP0002, ... EMP9999
        return f"EMP{next_number:04d}"

    @staticmethod
    def create_employee(db: Session, employee: EmployeeCreate) -> Employee:
        """Tạo employee mới với auto-generate code"""

        # Auto-generate employee code
        employee_code = EmployeeService.generate_employee_code(db)

        # Create employee
        db_employee = Employee(employee_code=employee_code, **employee.dict())

        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        return db_employee

    @staticmethod
    def get_employees(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        department_id: Optional[int] = None,
        position_id: Optional[int] = None,
        employment_status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> tuple[List[Employee], int]:
        """Lấy danh sách employees"""
        query = db.query(Employee)

        # Filters
        if department_id:
            query = query.filter(Employee.department_id == department_id)
        if position_id:
            query = query.filter(Employee.position_id == position_id)
        if employment_status:
            query = query.filter(Employee.employment_status == employment_status)
        if search:
            query = query.filter(
                (Employee.full_name.ilike(f"%{search}%"))
                | (Employee.email.ilike(f"%{search}%"))
                | (Employee.employee_code.ilike(f"%{search}%"))
            )

        total = query.count()
        employees = query.offset(skip).limit(limit).all()

        return employees, total

    @staticmethod
    def get_employee_by_id(db: Session, employee_id: int) -> Optional[Employee]:
        """Lấy employee theo ID"""
        return db.query(Employee).filter(Employee.id == employee_id).first()

    @staticmethod
    def get_employee_by_code(db: Session, employee_code: str) -> Optional[Employee]:
        """Lấy employee theo code"""
        return (
            db.query(Employee).filter(Employee.employee_code == employee_code).first()
        )

    @staticmethod
    def update_employee(
        db: Session, employee_id: int, employee_update: EmployeeUpdate
    ) -> Optional[Employee]:
        """Cập nhật employee"""
        db_employee = db.query(Employee).filter(Employee.id == employee_id).first()

        if not db_employee:
            return None

        update_data = employee_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_employee, key, value)

        db.commit()
        db.refresh(db_employee)
        return db_employee

    @staticmethod
    def get_subordinates(db: Session, manager_id: int) -> List[Employee]:
        """Lấy danh sách cấp dưới của manager"""
        return db.query(Employee).filter(Employee.direct_manager_id == manager_id).all()

    @staticmethod
    def terminate_employee(db: Session, employee_id: int) -> Optional[Employee]:
        """Chấm dứt hợp đồng employee"""
        db_employee = db.query(Employee).filter(Employee.id == employee_id).first()

        if not db_employee:
            return None

        db_employee.employment_status = "terminated"
        db.commit()
        db.refresh(db_employee)
        return db_employee
