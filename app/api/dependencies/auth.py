from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.config import settings
from app.models.user import User
from app.schemas.token import TokenData
from app.core.exceptions import UnauthorizedError, InactiveUserError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """
    Dependency: Lấy current user từ JWT token

    Raises:
        UnauthorizedError: Token không hợp lệ, hết hạn, hoặc user không tồn tại
        InactiveUserError: User bị vô hiệu hóa
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")

        if username is None:
            raise UnauthorizedError("Token không hợp lệ: thiếu thông tin username.")

        token_data = TokenData(username=username)

    except JWTError as e:
        raise UnauthorizedError(
            detail="Token không hợp lệ hoặc đã hết hạn. Vui lòng đăng nhập lại."
        )

    # Query user
    user = db.query(User).filter(User.username == token_data.username).first()

    if user is None:
        raise UnauthorizedError("User không tồn tại.")

    if not user.is_active:
        raise InactiveUserError()

    return user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency: Chỉ cho phép superuser

    Raises:
        PermissionDeniedError: Nếu user không phải superuser
    """
    if not current_user.is_superuser:
        from app.core.exceptions import PermissionDeniedError

        raise PermissionDeniedError(
            permission_name="superuser",
            detail="Chỉ quản trị viên (superuser) mới có quyền thực hiện hành động này.",
        )
    return current_user
