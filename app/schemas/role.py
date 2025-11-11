from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# Permission Schemas
class PermissionBase(BaseModel):
    name: str = Field(
        ..., max_length=100, description="Permission name (e.g., 'users:create')"
    )
    resource: str = Field(
        ..., max_length=50, description="Resource (e.g., 'users', 'orders')"
    )
    action: str = Field(
        ...,
        max_length=50,
        description="Action (e.g., 'create', 'read', 'update', 'delete')",
    )
    description: Optional[str] = Field(None, max_length=255)


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    description: Optional[str] = Field(None, max_length=255)


class Permission(PermissionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Role Schemas
class RoleBase(BaseModel):
    name: str = Field(..., max_length=50, description="Role name (e.g., 'QC_STAFF')")
    description: Optional[str] = Field(None, max_length=255)
    is_active: bool = True


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class Role(RoleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RoleWithPermissions(Role):
    """Role với danh sách permissions"""

    permissions: List[Permission] = []


class RoleAssignment(BaseModel):
    """Schema để assign role cho user"""

    role_id: int


class PermissionAssignment(BaseModel):
    """Schema để assign permission cho role"""

    permission_id: int
