"""
Seed script để khởi tạo dữ liệu mẫu cho hệ thống RBAC
Chạy: python -m app.scripts.seed_data
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.models import User, Role, Permission
from app.core.security import get_password_hash

# Import danh sách permissions, roles, mappings
PERMISSIONS = [
    {
        "name": "users:create",
        "resource": "users",
        "action": "create",
        "description": "Tạo user mới",
    },
    {
        "name": "users:read",
        "resource": "users",
        "action": "read",
        "description": "Xem thông tin user",
    },
    {
        "name": "users:update",
        "resource": "users",
        "action": "update",
        "description": "Cập nhật user",
    },
    {
        "name": "users:delete",
        "resource": "users",
        "action": "delete",
        "description": "Xóa user",
    },
    {
        "name": "orders:create",
        "resource": "orders",
        "action": "create",
        "description": "Tạo đơn hàng",
    },
    {
        "name": "orders:read",
        "resource": "orders",
        "action": "read",
        "description": "Xem đơn hàng",
    },
    {
        "name": "orders:update",
        "resource": "orders",
        "action": "update",
        "description": "Cập nhật đơn hàng",
    },
    {
        "name": "orders:delete",
        "resource": "orders",
        "action": "delete",
        "description": "Hủy đơn hàng",
    },
    {
        "name": "products:create",
        "resource": "products",
        "action": "create",
        "description": "Thêm sản phẩm",
    },
    {
        "name": "products:read",
        "resource": "products",
        "action": "read",
        "description": "Xem sản phẩm",
    },
    {
        "name": "products:update",
        "resource": "products",
        "action": "update",
        "description": "Cập nhật sản phẩm",
    },
    {
        "name": "products:delete",
        "resource": "products",
        "action": "delete",
        "description": "Xóa sản phẩm",
    },
    {
        "name": "inventory:manage",
        "resource": "inventory",
        "action": "manage",
        "description": "Quản lý tồn kho",
    },
    {
        "name": "qc:perform",
        "resource": "qc",
        "action": "perform",
        "description": "Thực hiện kiểm tra QC",
    },
    {
        "name": "qc:approve",
        "resource": "qc",
        "action": "approve",
        "description": "Duyệt kết quả QC",
    },
    {
        "name": "hr:read",
        "resource": "hr",
        "action": "read",
        "description": "Xem thông tin nhân sự",
    },
    {
        "name": "hr:update",
        "resource": "hr",
        "action": "update",
        "description": "Cập nhật thông tin nhân sự",
    },
    {
        "name": "hr:evaluate",
        "resource": "hr",
        "action": "evaluate",
        "description": "Đánh giá hiệu suất",
    },
]

ROLES = [
    {"name": "ADMIN", "description": "Administrator - Full access"},
    {"name": "QC_STAFF", "description": "QC Inspector - Quality Control"},
    {"name": "SALES_REP", "description": "Sales Representative - Orders"},
    {"name": "WAREHOUSE_STAFF", "description": "Warehouse Manager - Inventory"},
    {"name": "HR_STAFF", "description": "HR Manager - Human Resources"},
]

ROLE_PERMISSIONS = {
    "ADMIN": [
        "users:create",
        "users:read",
        "users:update",
        "users:delete",
        "orders:create",
        "orders:read",
        "orders:update",
        "orders:delete",
        "products:create",
        "products:read",
        "products:update",
        "products:delete",
        "inventory:manage",
        "qc:perform",
        "qc:approve",
        "hr:read",
        "hr:update",
        "hr:evaluate",
    ],
    "QC_STAFF": ["qc:perform", "products:read", "inventory:manage"],
    "SALES_REP": ["orders:create", "orders:read", "orders:update", "products:read"],
    "WAREHOUSE_STAFF": [
        "products:read",
        "products:update",
        "inventory:manage",
        "orders:read",
    ],
    "HR_STAFF": ["hr:read", "hr:update", "hr:evaluate", "users:read"],
}

TEST_USERS = [
    {
        "username": "qc_staff",
        "email": "qc@robis.com",
        "password": "qc123456",
        "full_name": "QC Inspector",
        "role": "QC_STAFF",
    },
    {
        "username": "sales_rep",
        "email": "sales@robis.com",
        "password": "sales123",
        "full_name": "Sales Representative",
        "role": "SALES_REP",
    },
    {
        "username": "warehouse",
        "email": "warehouse@robis.com",
        "password": "wh123456",
        "full_name": "Warehouse Manager",
        "role": "WAREHOUSE_STAFF",
    },
    {
        "username": "hr_staff",
        "email": "hr@robis.com",
        "password": "hr123456",
        "full_name": "HR Manager",
        "role": "HR_STAFF",
    },
]


def seed_permissions(db: Session):
    """Tạo tất cả permissions"""
    print("🌱 Seeding Permissions...")
    for perm_data in PERMISSIONS:
        existing = (
            db.query(Permission).filter(Permission.name == perm_data["name"]).first()
        )
        if not existing:
            perm = Permission(**perm_data)
            db.add(perm)
            print(f"  ✅ Created permission: {perm_data['name']}")
        else:
            print(f"  ⏭️  Permission already exists: {perm_data['name']}")
    db.commit()


def seed_roles(db: Session):
    """Tạo tất cả roles"""
    print("\n🌱 Seeding Roles...")
    for role_data in ROLES:
        existing = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing:
            role = Role(**role_data, is_active=True)
            db.add(role)
            print(f"  ✅ Created role: {role_data['name']}")
        else:
            print(f"  ⏭️  Role already exists: {role_data['name']}")
    db.commit()


def assign_permissions_to_roles(db: Session):
    """Gán permissions vào roles"""
    print("\n🔗 Assigning Permissions to Roles...")
    for role_name, perm_names in ROLE_PERMISSIONS.items():
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            print(f"  ⚠️  Role not found: {role_name}")
            continue

        for perm_name in perm_names:
            perm = db.query(Permission).filter(Permission.name == perm_name).first()
            if not perm:
                print(f"    ⚠️  Permission not found: {perm_name}")
                continue

            if perm not in role.permissions:
                role.permissions.append(perm)
                print(f"  ✅ Assigned {perm_name} to {role_name}")

    db.commit()


def seed_test_users(db: Session):
    """Tạo test users và gán roles"""
    print("\n👤 Seeding Test Users...")
    for user_data in TEST_USERS:
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if existing:
            print(f"  ⏭️  User already exists: {user_data['username']}")
            continue

        # Create user
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            hashed_password=get_password_hash(user_data["password"]),
            is_active=True,
            is_superuser=False,
        )
        db.add(user)
        db.flush()  # Get user.id

        # Assign role
        role = db.query(Role).filter(Role.name == user_data["role"]).first()
        if role:
            user.roles.append(role)
            print(
                f"  ✅ Created user: {user_data['username']} (Role: {user_data['role']})"
            )
        else:
            print(f"  ⚠️  Role not found for user: {user_data['username']}")

    db.commit()


def main():
    """Main seed function"""
    print("=" * 60)
    print("🚀 ROBIS ERP - SEED DATA SCRIPT")
    print("=" * 60)

    db = SessionLocal()

    try:
        seed_permissions(db)
        seed_roles(db)
        assign_permissions_to_roles(db)
        seed_test_users(db)

        print("\n" + "=" * 60)
        print("✅ SEED COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n📝 Test Users Created:")
        print("  - qc_staff / qc123456 (QC_STAFF)")
        print("  - sales_rep / sales123 (SALES_REP)")
        print("  - warehouse / wh123456 (WAREHOUSE_STAFF)")
        print("  - hr_staff / hr123456 (HR_STAFF)")
        print("\n🔐 Login with these credentials to test permissions!")

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
