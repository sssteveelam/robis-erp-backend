from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.role import Role, Permission
from app.models.user import User
from app.schemas.role import RoleCreate, RoleUpdate, PermissionCreate, PermissionUpdate


class RoleService:
    """Service xử lý nghiệp vụ roles"""

    @staticmethod
    def get_role(db: Session, role_id: int) -> Optional[Role]:
        """Lấy role theo ID"""
        return db.query(Role).filter(Role.id == role_id).first()

    @staticmethod
    def get_role_by_name(db: Session, name: str) -> Optional[Role]:
        """Lấy role theo name"""
        return db.query(Role).filter(Role.name == name).first()

    @staticmethod
    def get_roles(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[List[Role], int]:
        """Lấy danh sách roles"""
        query = db.query(Role)

        if search:
            query = query.filter(
                or_(
                    Role.name.ilike(f"%{search}%"),
                    Role.description.ilike(f"%{search}%"),
                )
            )

        if is_active is not None:
            query = query.filter(Role.is_active == is_active)

        total = query.count()
        roles = query.offset(skip).limit(limit).all()

        return roles, total

    @staticmethod
    def create_role(db: Session, role: RoleCreate) -> Role:
        """Tạo role mới"""
        db_role = Role(
            name=role.name, description=role.description, is_active=role.is_active
        )

        db.add(db_role)
        db.commit()
        db.refresh(db_role)

        return db_role

    @staticmethod
    def update_role(
        db: Session, role_id: int, role_update: RoleUpdate
    ) -> Optional[Role]:
        """Update role"""
        db_role = RoleService.get_role(db, role_id)

        if not db_role:
            return None

        update_data = role_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_role, field, value)

        db.commit()
        db.refresh(db_role)

        return db_role

    @staticmethod
    def delete_role(db: Session, role_id: int) -> bool:
        """Xóa role"""
        db_role = RoleService.get_role(db, role_id)

        if not db_role:
            return False

        db.delete(db_role)
        db.commit()

        return True

    @staticmethod
    def assign_permission_to_role(
        db: Session, role_id: int, permission_id: int
    ) -> Optional[Role]:
        """Gán permission cho role"""
        db_role = RoleService.get_role(db, role_id)
        db_permission = PermissionService.get_permission(db, permission_id)

        if not db_role or not db_permission:
            return None

        if db_permission not in db_role.permissions:
            db_role.permissions.append(db_permission)
            db.commit()
            db.refresh(db_role)

        return db_role

    @staticmethod
    def remove_permission_from_role(
        db: Session, role_id: int, permission_id: int
    ) -> Optional[Role]:
        """Gỡ permission khỏi role"""
        db_role = RoleService.get_role(db, role_id)
        db_permission = PermissionService.get_permission(db, permission_id)

        if not db_role or not db_permission:
            return None

        if db_permission in db_role.permissions:
            db_role.permissions.remove(db_permission)
            db.commit()
            db.refresh(db_role)

        return db_role

    @staticmethod
    def assign_role_to_user(db: Session, user_id: int, role_id: int) -> Optional[User]:
        """Gán role cho user"""
        from app.services.user_service import UserService

        db_user = UserService.get_user(db, user_id)
        db_role = RoleService.get_role(db, role_id)

        if not db_user or not db_role:
            return None

        if db_role not in db_user.roles:
            db_user.roles.append(db_role)
            db.commit()
            db.refresh(db_user)

        return db_user

    @staticmethod
    def remove_role_from_user(
        db: Session, user_id: int, role_id: int
    ) -> Optional[User]:
        """Gỡ role khỏi user"""
        from app.services.user_service import UserService

        db_user = UserService.get_user(db, user_id)
        db_role = RoleService.get_role(db, role_id)

        if not db_user or not db_role:
            return None

        if db_role in db_user.roles:
            db_user.roles.remove(db_role)
            db.commit()
            db.refresh(db_user)

        return db_user


class PermissionService:
    """Service xử lý nghiệp vụ permissions"""

    @staticmethod
    def get_permission(db: Session, permission_id: int) -> Optional[Permission]:
        """Lấy permission theo ID"""
        return db.query(Permission).filter(Permission.id == permission_id).first()

    @staticmethod
    def get_permission_by_name(db: Session, name: str) -> Optional[Permission]:
        """Lấy permission theo name"""
        return db.query(Permission).filter(Permission.name == name).first()

    @staticmethod
    def get_permissions(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        resource: Optional[str] = None,
        action: Optional[str] = None,
    ) -> tuple[List[Permission], int]:
        """Lấy danh sách permissions"""
        query = db.query(Permission)

        if resource:
            query = query.filter(Permission.resource == resource)

        if action:
            query = query.filter(Permission.action == action)

        total = query.count()
        permissions = query.offset(skip).limit(limit).all()

        return permissions, total

    @staticmethod
    def create_permission(db: Session, permission: PermissionCreate) -> Permission:
        """Tạo permission mới"""
        db_permission = Permission(
            name=permission.name,
            resource=permission.resource,
            action=permission.action,
            description=permission.description,
        )

        db.add(db_permission)
        db.commit()
        db.refresh(db_permission)

        return db_permission

    @staticmethod
    def update_permission(
        db: Session, permission_id: int, permission_update: PermissionUpdate
    ) -> Optional[Permission]:
        """Update permission"""
        db_permission = PermissionService.get_permission(db, permission_id)

        if not db_permission:
            return None

        update_data = permission_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_permission, field, value)

        db.commit()
        db.refresh(db_permission)

        return db_permission

    @staticmethod
    def delete_permission(db: Session, permission_id: int) -> bool:
        """Xóa permission"""
        db_permission = PermissionService.get_permission(db, permission_id)

        if not db_permission:
            return False

        db.delete(db_permission)
        db.commit()

        return True
