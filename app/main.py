from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, users  # Thêm users

# Khởi tạo FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Robis ERP Backend API - User Management System",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")  # Thêm dòng này


# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to Robis ERP API", "version": "1.0.0", "docs": "/docs"}


# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}
