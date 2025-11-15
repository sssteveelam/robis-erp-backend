"""
HR Schemas - Department, Position, Employee
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum


# ============= ENUMS =============


class DepartmentType(str, Enum):
    OPERATION = "operation"
    COMMERCIAL = "commercial"
    SUPPORT = "support"


class EmploymentStatus(str, Enum):
    ACTIVE = "active"
    PROBATION = "probation"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"


# ============= DEPARTMENT SCHEMAS =============


class DepartmentBase(BaseModel):
    name: str = Field(..., max_length=100)
    type: DepartmentType
    budget: Optional[float] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    type: Optional[DepartmentType] = None
    budget: Optional[float] = None


class Department(DepartmentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============= POSITION SCHEMAS =============


class PositionBase(BaseModel):
    title: str = Field(..., max_length=100)
    level: int = Field(..., ge=1, le=5)  # 1-5
    department_id: int
    description: Optional[str] = None


class PositionCreate(PositionBase):
    pass


class PositionUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    level: Optional[int] = Field(None, ge=1, le=5)
    department_id: Optional[int] = None
    description: Optional[str] = None


class Position(PositionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============= EMPLOYEE SCHEMAS =============


class EmployeeBase(BaseModel):
    full_name: str = Field(..., max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    department_id: int
    position_id: int
    direct_manager_id: Optional[int] = None
    hr_contact_id: Optional[int] = None
    hire_date: date
    employment_status: EmploymentStatus = EmploymentStatus.ACTIVE
    salary_range: Optional[str] = Field(None, max_length=50)


class EmployeeCreate(EmployeeBase):
    """Tạo employee mới - employee_code auto-generate"""

    user_id: Optional[int] = None


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    department_id: Optional[int] = None
    position_id: Optional[int] = None
    direct_manager_id: Optional[int] = None
    hr_contact_id: Optional[int] = None
    employment_status: Optional[EmploymentStatus] = None
    salary_range: Optional[str] = Field(None, max_length=50)


class Employee(EmployeeBase):
    id: int
    employee_code: str  # Auto-generated: EMP0001, EMP0002...
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeWithDetails(Employee):
    """Employee với thông tin department & position"""

    department: Optional[Department] = None
    position: Optional[Position] = None
    direct_manager: Optional[Employee] = None
