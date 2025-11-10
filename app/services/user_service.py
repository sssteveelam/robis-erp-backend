from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserService:
    """Service xử lý các nghiệp vụ quản lý users"""

    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """
        Lấy user theo ID

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User object hoặc None
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Lấy user theo username"""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Lấy user theo email"""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
    ) -> tuple[List[User], int]:
        """
        Lấy danh sách users với filtering và pagination

        Args:
            db: Database session
            skip: Số records bỏ qua (offset)
            limit: Số records tối đa trả về
            search: Tìm kiếm theo username hoặc email
            is_active: Filter theo trạng thái active
            is_superuser: Filter theo superuser

        Returns:
            Tuple (list users, total count)
        """
        query = db.query(User)

        # Apply filters
        if search:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%"),
                )
            )

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        if is_superuser is not None:
            query = query.filter(User.is_superuser == is_superuser)

        # Get total count before pagination
        total = query.count()

        # Apply pagination
        users = query.offset(skip).limit(limit).all()

        return users, total

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """
        Tạo user mới

        Args:
            db: Database session
            user: UserCreate schema

        Returns:
            User object vừa tạo
        """
        hashed_password = get_password_hash(user.password)

        db_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def update_user(
        db: Session, user_id: int, user_update: UserUpdate
    ) -> Optional[User]:
        """
        Update user

        Args:
            db: Database session
            user_id: User ID cần update
            user_update: UserUpdate schema với các fields cần update

        Returns:
            User object đã update hoặc None nếu không tìm thấy
        """
        db_user = UserService.get_user(db, user_id)

        if not db_user:
            return None

        # Update chỉ các fields không None
        update_data = user_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_user, field, value)

        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """
        Xóa user (soft delete bằng cách set is_active = False)

        Args:
            db: Database session
            user_id: User ID cần xóa

        Returns:
            True nếu xóa thành công, False nếu không tìm thấy user
        """
        db_user = UserService.get_user(db, user_id)

        if not db_user:
            return False

        # Soft delete: Chỉ set is_active = False
        db_user.is_active = False
        db.commit()

        return True

    @staticmethod
    def hard_delete_user(db: Session, user_id: int) -> bool:
        """
        Xóa vĩnh viễn user khỏi database (chỉ superuser)

        Args:
            db: Database session
            user_id: User ID cần xóa

        Returns:
            True nếu xóa thành công, False nếu không tìm thấy user
        """
        db_user = UserService.get_user(db, user_id)

        if not db_user:
            return False

        db.delete(db_user)
        db.commit()

        return True

    @staticmethod
    def activate_user(db: Session, user_id: int, is_active: bool) -> Optional[User]:
        """
        Kích hoạt hoặc vô hiệu hóa user

        Args:
            db: Database session
            user_id: User ID
            is_active: True để kích hoạt, False để vô hiệu hóa

        Returns:
            User object đã update hoặc None
        """
        db_user = UserService.get_user(db, user_id)

        if not db_user:
            return None

        db_user.is_active = is_active
        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def set_superuser(db: Session, user_id: int, is_superuser: bool) -> Optional[User]:
        """
        Đặt hoặc bỏ quyền superuser

        Args:
            db: Database session
            user_id: User ID
            is_superuser: True để set superuser, False để bỏ

        Returns:
            User object đã update hoặc None
        """
        db_user = UserService.get_user(db, user_id)

        if not db_user:
            return None

        db_user.is_superuser = is_superuser
        db.commit()
        db.refresh(db_user)

        return db_user
