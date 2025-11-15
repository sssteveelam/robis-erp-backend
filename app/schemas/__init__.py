from app.schemas.user import User, UserCreate, UserUpdate
from app.schemas.role import Role, RoleCreate, Permission, PermissionCreate
from app.schemas.customer import Customer, CustomerCreate, CustomerUpdate
from app.schemas.order import (
    Order,
    OrderCreate,
    OrderUpdate,
    OrderItem,
    OrderItemCreate,
)
from app.schemas.product import (
    Product,
    ProductCreate,
    ProductUpdate,
    ProductCategory,
    ProductCategoryCreate,
    ProductCategoryUpdate,
)
from app.schemas.inventory import (
    Batch,
    BatchCreate,
    BatchUpdate,
    Warehouse,
    WarehouseCreate,
    Stock,
    StockMovement,
    StockMovementCreate,
    QCCheckpoint,
    QCCheckpointCreate,
)
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
from app.schemas.attendance import (
    Attendance,
    AttendanceCheckIn,
    AttendanceCheckOut,
    AttendanceLeaveRequest,
    AttendanceReport,
)
from app.schemas.performance import (
    PerformanceReview,
    PerformanceReviewCreate,
    PerformanceReviewUpdate,
    PerformanceReviewWithDetails,
)
from app.schemas.common import PaginatedResponse

__all__ = [
    # User & Auth
    "User",
    "UserCreate",
    "UserUpdate",
    "Role",
    "RoleCreate",
    "Permission",
    "PermissionCreate",
    # Customer & Orders
    "Customer",
    "CustomerCreate",
    "CustomerUpdate",
    "Order",
    "OrderCreate",
    "OrderUpdate",
    "OrderItem",
    "OrderItemCreate",
    # Products
    "Product",
    "ProductCreate",
    "ProductUpdate",
    "ProductCategory",
    "ProductCategoryCreate",
    "ProductCategoryUpdate",
    # Inventory
    "Batch",
    "BatchCreate",
    "BatchUpdate",
    "Warehouse",
    "WarehouseCreate",
    "Stock",
    "StockMovement",
    "StockMovementCreate",
    "QCCheckpoint",
    "QCCheckpointCreate",
    # HR
    "Department",
    "DepartmentCreate",
    "DepartmentUpdate",
    "Position",
    "PositionCreate",
    "PositionUpdate",
    "Employee",
    "EmployeeCreate",
    "EmployeeUpdate",
    "EmployeeWithDetails",
    # Attendance
    "Attendance",
    "AttendanceCheckIn",
    "AttendanceCheckOut",
    "AttendanceLeaveRequest",
    "AttendanceReport",
    # Performance
    "PerformanceReview",
    "PerformanceReviewCreate",
    "PerformanceReviewUpdate",
    "PerformanceReviewWithDetails",
    # Common
    "PaginatedResponse",
]
