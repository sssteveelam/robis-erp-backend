"""
Product Service - Business Logic
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, Tuple, List
from datetime import datetime

from app.models.product import Product, ProductCategory
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductCategoryCreate,
    ProductCategoryUpdate,
)


class ProductCategoryService:

    @staticmethod
    def create_category(
        db: Session, category: ProductCategoryCreate
    ) -> ProductCategory:
        """Tạo category mới"""
        db_category = ProductCategory(
            name=category.name, description=category.description, is_active=True
        )
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category

    @staticmethod
    def get_categories(
        db: Session, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None
    ) -> Tuple[List[ProductCategory], int]:
        """Lấy danh sách categories"""
        query = db.query(ProductCategory)

        if is_active is not None:
            query = query.filter(ProductCategory.is_active == is_active)

        total = query.count()
        categories = query.offset(skip).limit(limit).all()

        return categories, total


class ProductService:

    @staticmethod
    def create_product(db: Session, product: ProductCreate) -> Product:
        """Tạo product mới"""
        # Check duplicate SKU
        existing = db.query(Product).filter(Product.sku == product.sku).first()
        if existing:
            raise ValueError(f"Product với SKU {product.sku} đã tồn tại")

        db_product = Product(
            sku=product.sku,
            name=product.name,
            description=product.description,
            category_id=product.category_id,
            unit_price=product.unit_price,
            cost_price=product.cost_price,
            unit=product.unit,
            min_stock=product.min_stock,
            max_stock=product.max_stock,
            is_active=True,
        )

        db.add(db_product)
        db.commit()
        db.refresh(db_product)

        return db_product

    @staticmethod
    def get_products(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[Product], int]:
        """Lấy danh sách products"""
        query = db.query(Product)

        # Search
        if search:
            query = query.filter(
                or_(Product.sku.ilike(f"%{search}%"), Product.name.ilike(f"%{search}%"))
            )

        # Filter by category
        if category_id:
            query = query.filter(Product.category_id == category_id)

        # Filter by active status
        if is_active is not None:
            query = query.filter(Product.is_active == is_active)

        total = query.count()
        products = (
            query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
        )

        return products, total

    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        """Lấy product theo ID"""
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def update_product(
        db: Session, product_id: int, product_update: ProductUpdate
    ) -> Optional[Product]:
        """Update product"""
        db_product = ProductService.get_product_by_id(db, product_id)

        if not db_product:
            return None

        update_data = product_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)

        db_product.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_product)

        return db_product

    @staticmethod
    def check_low_stock(db: Session) -> List[Product]:
        """Kiểm tra sản phẩm tồn kho thấp"""
        from app.models.inventory import Stock
        from sqlalchemy import func

        # Subquery để tính tổng tồn kho của mỗi product
        stock_subquery = (
            db.query(Stock.product_id, func.sum(Stock.quantity).label("total_quantity"))
            .group_by(Stock.product_id)
            .subquery()
        )

        # Join với products và filter
        low_stock_products = (
            db.query(Product)
            .join(stock_subquery, Product.id == stock_subquery.c.product_id)
            .filter(stock_subquery.c.total_quantity < Product.min_stock)
            .all()
        )

        return low_stock_products
