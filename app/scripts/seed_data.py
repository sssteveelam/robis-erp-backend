"""
Seed initial data for development
"""

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User
from app.models.role import Role, Permission
from app.models.product import Product, ProductCategory
from app.models.inventory import Warehouse, Batch
from app.core.security import get_password_hash
from datetime import date, timedelta


def clear_all_data(db: Session):
    """Xóa toàn bộ data (OPTIONAL)"""
    print("Clearing all existing data...")

    # Xóa theo thứ tự (foreign keys)
    db.query(User).delete()
    db.execute("DELETE FROM user_roles")
    db.execute("DELETE FROM role_permissions")
    db.query(Role).delete()
    db.query(Permission).delete()

    db.commit()
    print("✅ Data cleared!\n")


def seed_roles_and_permissions(db: Session):
    """Seed roles and permissions"""
    print("Seeding roles and permissions...")

    # Define permissions with resource and action
    permissions_data = [
        # Orders permissions
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
            "description": "Xóa đơn hàng",
        },
        # QC permissions
        {
            "name": "qc:perform",
            "resource": "qc",
            "action": "perform",
            "description": "Thực hiện QC",
        },
        # Products permissions
        {
            "name": "products:create",
            "resource": "products",
            "action": "create",
            "description": "Tạo sản phẩm",
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
        # Inventory permissions
        {
            "name": "inventory:manage",
            "resource": "inventory",
            "action": "manage",
            "description": "Quản lý kho",
        },
        {
            "name": "inventory:read",
            "resource": "inventory",
            "action": "read",
            "description": "Xem kho",
        },
        # HR permissions
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
            "description": "Đánh giá nhân viên",
        },
        # User management permissions
        {
            "name": "users:manage",
            "resource": "users",
            "action": "manage",
            "description": "Quản lý người dùng",
        },
        {
            "name": "roles:manage",
            "resource": "roles",
            "action": "manage",
            "description": "Quản lý vai trò",
        },
    ]

    permissions = {}
    for perm_data in permissions_data:
        existing = (
            db.query(Permission).filter(Permission.name == perm_data["name"]).first()
        )
        if not existing:
            permission = Permission(
                name=perm_data["name"],
                resource=perm_data["resource"],
                action=perm_data["action"],
                description=perm_data["description"],
            )
            db.add(permission)
            db.flush()
            permissions[perm_data["name"]] = permission
            print(f"  ✓ Created permission: {perm_data['name']}")
        else:
            permissions[perm_data["name"]] = existing

    # Define roles - ĐÃ FIX ĐẦY ĐỦ PERMISSIONS
    roles_data = [
        {
            "name": "QC_STAFF",
            "description": "Nhân viên QC",
            "permissions": ["qc:perform", "products:read", "inventory:read"],
        },
        {
            "name": "SALES_REP",
            "description": "Nhân viên kinh doanh",
            "permissions": [
                "orders:create",
                "orders:read",
                "orders:update",
                "products:read",
            ],
        },
        {
            "name": "WAREHOUSE_STAFF",
            "description": "Nhân viên kho",
            "permissions": [
                "inventory:manage",  # ← CÓ
                "inventory:read",  # ← CÓ
                "products:create",  # ← CÓ
                "products:read",  # ← CÓ
                "products:update",  # ← CÓ
            ],
        },
        {
            "name": "HR_STAFF",
            "description": "Nhân viên nhân sự",
            "permissions": ["hr:read", "hr:update", "hr:evaluate"],
        },
    ]

    roles = {}
    for role_data in roles_data:
        existing = db.query(Role).filter(Role.name == role_data["name"]).first()

        if not existing:
            role = Role(name=role_data["name"], description=role_data["description"])
            db.add(role)
            db.flush()

            # Assign permissions
            for perm_name in role_data["permissions"]:
                if perm_name in permissions:
                    role.permissions.append(permissions[perm_name])

            roles[role_data["name"]] = role
            print(
                f"  ✓ Created role: {role_data['name']} with {len(role_data['permissions'])} permissions"
            )
        else:
            # UPDATE existing role permissions
            existing.permissions.clear()
            for perm_name in role_data["permissions"]:
                if perm_name in permissions:
                    existing.permissions.append(permissions[perm_name])
            roles[role_data["name"]] = existing
            print(
                f"  ✓ Updated role: {role_data['name']} with {len(role_data['permissions'])} permissions"
            )

    db.commit()
    print("✅ Roles and permissions seeded!\n")
    return roles


def seed_test_users(db: Session):
    """Seed test users"""
    print("Seeding test users...")

    # Get roles
    qc_role = db.query(Role).filter(Role.name == "QC_STAFF").first()
    sales_role = db.query(Role).filter(Role.name == "SALES_REP").first()
    warehouse_role = db.query(Role).filter(Role.name == "WAREHOUSE_STAFF").first()
    hr_role = db.query(Role).filter(Role.name == "HR_STAFF").first()

    users_data = [
        {
            "username": "qc_staff",
            "email": "qc@robis.com",
            "full_name": "QC Staff",
            "password": "qc123456",
            "role": qc_role,
        },
        {
            "username": "sales_rep",
            "email": "sales@robis.com",
            "full_name": "Sales Representative",
            "password": "sales123",
            "role": sales_role,
        },
        {
            "username": "warehouse",
            "email": "warehouse@robis.com",
            "full_name": "Warehouse Staff",
            "password": "wh123456",
            "role": warehouse_role,
        },
        {
            "username": "hr_staff",
            "email": "hr@robis.com",
            "full_name": "HR Staff",
            "password": "hr123456",
            "role": hr_role,
        },
    ]

    for user_data in users_data:
        existing = db.query(User).filter(User.username == user_data["username"]).first()

        if not existing:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=get_password_hash(user_data["password"]),
                is_active=True,
                is_superuser=False,
            )
            db.add(user)
            db.flush()

            if user_data["role"]:
                user.roles.append(user_data["role"])

            print(
                f"  ✓ Created user: {user_data['username']} (password: {user_data['password']})"
            )
        else:
            print(f"  → User {user_data['username']} already exists")

    db.commit()
    print("✅ Test users seeded!\n")


def seed_inventory_data(db: Session):
    """Seed sample inventory data"""
    print("Seeding inventory data...")

    # 1. Create Product Categories
    categories_data = [
        {"name": "Thực phẩm", "description": "Thực phẩm đóng gói"},
        {"name": "Đồ uống", "description": "Nước giải khát, nước trái cây"},
        {"name": "Gia vị", "description": "Gia vị, nước sốt"},
        {"name": "Nguyên liệu", "description": "Nguyên liệu chế biến"},
    ]

    categories = {}
    for cat_data in categories_data:
        existing = (
            db.query(ProductCategory)
            .filter(ProductCategory.name == cat_data["name"])
            .first()
        )

        if not existing:
            category = ProductCategory(**cat_data)
            db.add(category)
            db.flush()
            categories[cat_data["name"]] = category
            print(f"  ✓ Created category: {cat_data['name']}")
        else:
            categories[cat_data["name"]] = existing

    # 2. Create Products
    products_data = [
        {
            "sku": "SP-001",
            "name": "Bánh mì sandwich",
            "description": "Bánh mì sandwich đóng gói",
            "category_id": categories["Thực phẩm"].id,
            "unit_price": 25000,
            "cost_price": 15000,
            "unit": "pcs",
            "min_stock": 50,
            "max_stock": 500,
        },
        {
            "sku": "SP-002",
            "name": "Nước cam ép",
            "description": "Nước cam ép tươi 500ml",
            "category_id": categories["Đồ uống"].id,
            "unit_price": 30000,
            "cost_price": 20000,
            "unit": "bottle",
            "min_stock": 100,
            "max_stock": 1000,
        },
        {
            "sku": "SP-003",
            "name": "Sốt tương ớt",
            "description": "Tương ớt Cholimex 270g",
            "category_id": categories["Gia vị"].id,
            "unit_price": 18000,
            "cost_price": 12000,
            "unit": "bottle",
            "min_stock": 30,
            "max_stock": 300,
        },
        {
            "sku": "SP-004",
            "name": "Gạo ST25",
            "description": "Gạo ST25 cao cấp",
            "category_id": categories["Nguyên liệu"].id,
            "unit_price": 45000,
            "cost_price": 35000,
            "unit": "kg",
            "min_stock": 200,
            "max_stock": 2000,
        },
        {
            "sku": "SP-005",
            "name": "Sữa tươi Vinamilk",
            "description": "Sữa tươi 1L không đường",
            "category_id": categories["Đồ uống"].id,
            "unit_price": 35000,
            "cost_price": 28000,
            "unit": "bottle",
            "min_stock": 80,
            "max_stock": 800,
        },
    ]

    products = {}
    for prod_data in products_data:
        existing = db.query(Product).filter(Product.sku == prod_data["sku"]).first()

        if not existing:
            product = Product(**prod_data)
            db.add(product)
            db.flush()
            products[prod_data["sku"]] = product
            print(f"  ✓ Created product: {prod_data['sku']} - {prod_data['name']}")
        else:
            products[prod_data["sku"]] = existing

    # 3. Create Warehouses
    warehouses_data = [
        {
            "code": "WH-HN",
            "name": "Kho Hà Nội",
            "address": "123 Đường Láng, Đống Đa, Hà Nội",
        },
        {
            "code": "WH-HCM",
            "name": "Kho TP.HCM",
            "address": "456 Nguyễn Văn Linh, Quận 7, TP.HCM",
        },
        {
            "code": "WH-DN",
            "name": "Kho Đà Nẵng",
            "address": "789 Hùng Vương, Hải Châu, Đà Nẵng",
        },
    ]

    warehouses = {}
    for wh_data in warehouses_data:
        existing = db.query(Warehouse).filter(Warehouse.code == wh_data["code"]).first()

        if not existing:
            warehouse = Warehouse(**wh_data)
            db.add(warehouse)
            db.flush()
            warehouses[wh_data["code"]] = warehouse
            print(f"  ✓ Created warehouse: {wh_data['code']} - {wh_data['name']}")
        else:
            warehouses[wh_data["code"]] = existing

    # 4. Create Sample Batches
    today = date.today()
    batches_data = [
        {
            "batch_number": "BATCH-001",
            "product_id": products["SP-001"].id,
            "initial_quantity": 200,
            "current_quantity": 200,
            "manufacturing_date": today - timedelta(days=5),
            "expiry_date": today + timedelta(days=25),
            "qc_status": "passed",
        },
        {
            "batch_number": "BATCH-002",
            "product_id": products["SP-002"].id,
            "initial_quantity": 500,
            "current_quantity": 500,
            "manufacturing_date": today - timedelta(days=3),
            "expiry_date": today + timedelta(days=60),
            "qc_status": "passed",
        },
        {
            "batch_number": "BATCH-003",
            "product_id": products["SP-003"].id,
            "initial_quantity": 150,
            "current_quantity": 150,
            "manufacturing_date": today - timedelta(days=10),
            "expiry_date": today + timedelta(days=350),
            "qc_status": "passed",
        },
    ]

    for batch_data in batches_data:
        existing = (
            db.query(Batch)
            .filter(Batch.batch_number == batch_data["batch_number"])
            .first()
        )

        if not existing:
            batch = Batch(**batch_data)
            db.add(batch)
            print(f"  ✓ Created batch: {batch_data['batch_number']}")

    db.commit()
    print("✅ Inventory data seeded successfully!\n")


def main():
    """Main seed function"""
    db = SessionLocal()

    try:
        # OPTION: Clear all data first (UNCOMMENT nếu muốn reset)
        # clear_all_data(db)

        # Seed data
        seed_roles_and_permissions(db)
        seed_test_users(db)
        seed_inventory_data(db)

        print("=" * 50)
        print("🎉 ALL DATA SEEDED SUCCESSFULLY!")
        print("=" * 50)
        print("\n📋 Test Users:")
        print("  - warehouse / wh123456 (WAREHOUSE_STAFF - 5 permissions)")
        print("  - qc_staff / qc123456 (QC_STAFF)")
        print("  - sales_rep / sales123 (SALES_REP)")
        print("  - hr_staff / hr123456 (HR_STAFF)")

    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        import traceback

        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
