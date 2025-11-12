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
)


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


@app.get("/")
def read_root():
    return {"message": "Welcome to Robis ERP API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
