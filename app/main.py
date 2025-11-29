from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import (
    auth,
    users,
    roles,
    permissions,
    customers,
    orders,
    products,
    inventory,
    qc,
    hr,
    attendance,
    performance,
    public_attendance,
)
from app.api.v1.endpoints import ai

# Auto-run Alembic migrations on startup (safe if already at head)
import os
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig

def run_db_migrations():
    try:
        # Resolve alembic.ini relative to project root
        current_dir = os.path.dirname(__file__)  # app/
        alembic_ini = os.path.normpath(os.path.join(current_dir, "..", "alembic.ini"))
        if not os.path.exists(alembic_ini):
            # Fallback to CWD
            alembic_ini = "alembic.ini"
        cfg = AlembicConfig(alembic_ini)
        alembic_command.upgrade(cfg, "head")
    except Exception as e:
        # Log and continue startup; avoids blocking app if migration is no-op or already applied
        print(f"[Startup] Alembic migration skipped/error: {e}")

app = FastAPI(
    title="Robis ERP Backend API",
    description="""
## Robis ERP Backend API

Hệ thống quản lý ERP cho Robis, bao gồm:

**Authentication & Authorization**: JWT-based với RBAC  
**User Management**: Quản lý người dùng, roles, permissions  
**Orders Module**: Quản lý đơn hàng B2C/B2B  
**Inventory Module**: Quản lý tồn kho với FEFO  
**HR Module**: Quản lý nhân sự và đánh giá hiệu suất

### Phân quyền

Hệ thống sử dụng Role-Based Access Control (RBAC):
- **Superuser**: Có mọi quyền trong hệ thống
- **Roles**: Admin, QC_STAFF, SALES_REP, WAREHOUSE_STAFF, HR_STAFF
- **Permissions**: Từng quyền cụ thể (VD: orders:create, qc:perform)

### Error Codes

- **401 Unauthorized**: Chưa đăng nhập hoặc token không hợp lệ
- **403 Forbidden**: Không có quyền thực hiện hành động
- **404 Not Found**: Resource không tồn tại
- **400 Bad Request**: Dữ liệu không hợp lệ
- **422 Validation Error**: Dữ liệu không đúng format
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Run DB migrations automatically on startup (idempotent)
@app.on_event("startup")
async def _run_migrations_on_startup():
    run_db_migrations()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Dữ liệu không hợp lệ", "errors": exc.errors()},
    )


app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(roles.router, prefix="/api/v1")
app.include_router(permissions.router, prefix="/api/v1")
app.include_router(customers.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(inventory.router, prefix="/api/v1")
app.include_router(qc.router, prefix="/api/v1")
# HR Module Routes
app.include_router(hr.router, prefix="/api/v1", tags=["HR"])
app.include_router(attendance.router, prefix="/api/v1", tags=["Attendance"])
app.include_router(performance.router, prefix="/api/v1", tags=["Performance Reviews"])
# Public Attendance Routes (QR/Kiosk - NEW)
app.include_router(public_attendance.router)
# AI Module Routes (NEW)
app.include_router(ai.router, prefix="/api/v1", tags=["AI Assistant"])


@app.get("/")
def read_root():
    return {"message": "Welcome to Robis ERP API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
