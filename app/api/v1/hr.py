"""
HR API Endpoints - Departments, Positions, Employees
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.schemas.hr import (
    Department,
    DepartmentCreate,
    DepartmentUpdate,
    Position,
    PositionCreate,
    PositionUpdate,
    Employee,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeWithDetails,
)
from app.schemas.common import PaginatedResponse
from app.services.hr_service import DepartmentService, PositionService, EmployeeService
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.models.user import User as UserModel

router = APIRouter(tags=["HR"])


# ============= DEPARTMENT ENDPOINTS =============


@router.post(
    "/departments",
    response_model=Department,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission("hr:manage")],
)
def create_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Tạo department mới

    Permission: hr:manage
    Roles: HR_STAFF, ADMIN
    """
    return DepartmentService.create_department(db, department)


@router.get(
    "/departments",
    response_model=PaginatedResponse[Department],
    dependencies=[require_permission("hr:read")],
)
def get_departments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=100),
    type: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Lấy danh sách departments

    Permission: hr:read
    Roles: Tất cả authenticated users
    """
    skip = (page - 1) * page_size

    departments, total = DepartmentService.get_departments(
        db=db, skip=skip, limit=page_size, type=type
    )

    return PaginatedResponse.create(
        items=departments, total=total, page=page, page_size=page_size
    )


@router.get(
    "/departments/{department_id}",
    response_model=Department,
    dependencies=[require_permission("hr:read")],
)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Lấy department theo ID"""
    department = DepartmentService.get_department_by_id(db, department_id)

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department với ID {department_id} không tồn tại",
        )

    return department


@router.put(
    "/departments/{department_id}",
    response_model=Department,
    dependencies=[require_permission("hr:manage")],
)
def update_department(
    department_id: int,
    department_update: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Cập nhật department"""
    department = DepartmentService.update_department(
        db, department_id, department_update
    )

    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department với ID {department_id} không tồn tại",
        )

    return department


# ============= POSITION ENDPOINTS =============


@router.post(
    "/positions",
    response_model=Position,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission("hr:manage")],
)
def create_position(
    position: PositionCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Tạo position mới"""
    return PositionService.create_position(db, position)


@router.get(
    "/positions",
    response_model=PaginatedResponse[Position],
    dependencies=[require_permission("hr:read")],
)
def get_positions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=100),
    department_id: Optional[int] = Query(default=None),
    level: Optional[int] = Query(default=None, ge=1, le=5),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Lấy danh sách positions"""
    skip = (page - 1) * page_size

    positions, total = PositionService.get_positions(
        db=db, skip=skip, limit=page_size, department_id=department_id, level=level
    )

    return PaginatedResponse.create(
        items=positions, total=total, page=page, page_size=page_size
    )


@router.get(
    "/positions/{position_id}",
    response_model=Position,
    dependencies=[require_permission("hr:read")],
)
def get_position(
    position_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Lấy position theo ID"""
    position = PositionService.get_position_by_id(db, position_id)

    if not position:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Position với ID {position_id} không tồn tại",
        )

    return position


@router.get(
    "/positions/{position_id}/career-path",
    response_model=list[Position],
    dependencies=[require_permission("hr:read")],
)
def get_career_path(
    position_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Lấy lộ trình thăng tiến (career path)

    Trả về các positions trong cùng department với level cao hơn
    """
    return PositionService.get_career_path(db, position_id)


# ============= EMPLOYEE ENDPOINTS =============


@router.post(
    "/employees",
    response_model=Employee,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission("hr:manage")],
)
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Tạo employee mới

    Employee code sẽ được auto-generate: EMP0001, EMP0002, ...
    """
    try:
        return EmployeeService.create_employee(db, employee)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/employees",
    response_model=PaginatedResponse[Employee],
    dependencies=[require_permission("hr:read")],
)
def get_employees(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    department_id: Optional[int] = Query(default=None),
    position_id: Optional[int] = Query(default=None),
    employment_status: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Lấy danh sách employees

    Search: Tìm theo name, email, employee_code
    """
    skip = (page - 1) * page_size

    employees, total = EmployeeService.get_employees(
        db=db,
        skip=skip,
        limit=page_size,
        department_id=department_id,
        position_id=position_id,
        employment_status=employment_status,
        search=search,
    )

    return PaginatedResponse.create(
        items=employees, total=total, page=page, page_size=page_size
    )


@router.get(
    "/employees/{employee_id}",
    response_model=Employee,
    dependencies=[require_permission("hr:read")],
)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Lấy employee theo ID"""
    employee = EmployeeService.get_employee_by_id(db, employee_id)

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee với ID {employee_id} không tồn tại",
        )

    return employee


@router.put(
    "/employees/{employee_id}",
    response_model=Employee,
    dependencies=[require_permission("hr:manage")],
)
def update_employee(
    employee_id: int,
    employee_update: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Cập nhật employee"""
    employee = EmployeeService.update_employee(db, employee_id, employee_update)

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee với ID {employee_id} không tồn tại",
        )

    return employee


@router.get(
    "/employees/{employee_id}/subordinates",
    response_model=list[Employee],
    dependencies=[require_permission("hr:read")],
)
def get_subordinates(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Lấy danh sách cấp dưới của manager"""
    return EmployeeService.get_subordinates(db, employee_id)


@router.post(
    "/employees/{employee_id}/terminate",
    response_model=Employee,
    dependencies=[require_permission("hr:manage")],
)
def terminate_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Chấm dứt hợp đồng employee"""
    employee = EmployeeService.terminate_employee(db, employee_id)

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee với ID {employee_id} không tồn tại",
        )

    return employee
