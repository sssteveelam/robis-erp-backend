"""
Inventory Service - Stock, Batch, Movement
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List, Tuple
from datetime import datetime, date

from app.models.inventory import Batch, Warehouse, Stock, StockMovement, MovementType
from app.models.product import Product
from app.schemas.inventory import BatchCreate, WarehouseCreate, StockMovementCreate


class WarehouseService:

    @staticmethod
    def create_warehouse(db: Session, warehouse: WarehouseCreate) -> Warehouse:
        """Tạo warehouse mới"""
        db_warehouse = Warehouse(
            code=warehouse.code,
            name=warehouse.name,
            address=warehouse.address,
            is_active=True,
        )
        db.add(db_warehouse)
        db.commit()
        db.refresh(db_warehouse)
        return db_warehouse

    @staticmethod
    def get_warehouses(
        db: Session, is_active: Optional[bool] = None
    ) -> List[Warehouse]:
        """Lấy danh sách warehouses"""
        query = db.query(Warehouse)
        if is_active is not None:
            query = query.filter(Warehouse.is_active == is_active)
        return query.all()


class BatchService:

    @staticmethod
    def generate_batch_number(db: Session) -> str:
        """Generate unique batch number"""
        today = datetime.now().strftime("%Y%m%d")
        count = (
            db.query(Batch).filter(Batch.batch_number.like(f"BATCH-{today}-%")).count()
        )
        sequence = str(count + 1).zfill(4)
        return f"BATCH-{today}-{sequence}"

    @staticmethod
    def create_batch(db: Session, batch: BatchCreate) -> Batch:
        """Tạo batch mới"""
        batch_number = BatchService.generate_batch_number(db)

        db_batch = Batch(
            batch_number=batch_number,
            product_id=batch.product_id,
            initial_quantity=batch.initial_quantity,
            current_quantity=batch.initial_quantity,
            manufacturing_date=batch.manufacturing_date,
            expiry_date=batch.expiry_date,
            qc_status="pending",
            is_active=True,
        )

        db.add(db_batch)
        db.commit()
        db.refresh(db_batch)

        return db_batch

    @staticmethod
    def get_batches_by_product(
        db: Session, product_id: int, qc_status: Optional[str] = None
    ) -> List[Batch]:
        """Lấy batches theo product"""
        query = db.query(Batch).filter(Batch.product_id == product_id)

        if qc_status:
            query = query.filter(Batch.qc_status == qc_status)

        return query.filter(Batch.is_active == True).all()

    @staticmethod
    def get_batches_fefo(
        db: Session, product_id: int, warehouse_id: Optional[int] = None
    ) -> List[Batch]:
        """
        Lấy batches theo FEFO (First Expiry First Out)
        Ưu tiên: QC passed, còn hàng, hạn sử dụng gần nhất
        """
        query = db.query(Batch).filter(
            Batch.product_id == product_id,
            Batch.qc_status == "passed",
            Batch.current_quantity > 0,
            Batch.is_active == True,
        )

        # Sort by expiry_date (FEFO)
        return query.order_by(Batch.expiry_date.asc()).all()


class StockService:

    @staticmethod
    def get_stock(db: Session, warehouse_id: int, product_id: int) -> Optional[Stock]:
        """Lấy stock record"""
        return (
            db.query(Stock)
            .filter(Stock.warehouse_id == warehouse_id, Stock.product_id == product_id)
            .first()
        )

    @staticmethod
    def get_or_create_stock(db: Session, warehouse_id: int, product_id: int) -> Stock:
        """Lấy hoặc tạo stock record"""
        stock = StockService.get_stock(db, warehouse_id, product_id)

        if not stock:
            stock = Stock(warehouse_id=warehouse_id, product_id=product_id, quantity=0)
            db.add(stock)
            db.flush()

        return stock

    @staticmethod
    def get_stock_summary(db: Session, product_id: Optional[int] = None):
        """Tổng hợp tồn kho"""
        query = db.query(
            Stock.product_id,
            Product.sku,
            Product.name,
            func.sum(Stock.quantity).label("total_quantity"),
        ).join(Product)

        if product_id:
            query = query.filter(Stock.product_id == product_id)

        return query.group_by(Stock.product_id, Product.sku, Product.name).all()


class StockMovementService:

    @staticmethod
    def generate_movement_number(db: Session, movement_type: str) -> str:
        """Generate movement number"""
        prefix = {
            "import": "IMP",
            "export": "EXP",
            "check": "CHK",
            "transfer": "TRF",
            "adjust": "ADJ",
        }.get(movement_type, "MOV")

        today = datetime.now().strftime("%Y%m%d")
        count = (
            db.query(StockMovement)
            .filter(StockMovement.movement_number.like(f"{prefix}-{today}-%"))
            .count()
        )
        sequence = str(count + 1).zfill(4)
        return f"{prefix}-{today}-{sequence}"

    @staticmethod
    def import_stock(
        db: Session, movement: StockMovementCreate, created_by: int
    ) -> StockMovement:
        """
        Nhập kho
        - Tạo stock movement
        - Cập nhật stock quantity
        - Cập nhật batch quantity (nếu có)
        """
        movement_number = StockMovementService.generate_movement_number(
            db, movement.movement_type
        )

        # Create movement
        db_movement = StockMovement(
            movement_number=movement_number,
            movement_type=MovementType(movement.movement_type),
            product_id=movement.product_id,
            batch_id=movement.batch_id,
            warehouse_id=movement.warehouse_id,
            quantity=movement.quantity,
            reference_type=movement.reference_type,
            reference_id=movement.reference_id,
            note=movement.note,
            created_by=created_by,
        )
        db.add(db_movement)

        # Update stock
        stock = StockService.get_or_create_stock(
            db, movement.warehouse_id, movement.product_id
        )
        stock.quantity += movement.quantity
        stock.updated_at = datetime.utcnow()

        # Update batch if specified
        if movement.batch_id:
            batch = db.query(Batch).filter(Batch.id == movement.batch_id).first()
            if batch:
                batch.current_quantity += movement.quantity
                batch.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(db_movement)

        return db_movement

    @staticmethod
    def export_stock(
        db: Session, movement: StockMovementCreate, created_by: int
    ) -> StockMovement:
        """
        Xuất kho
        - Kiểm tra đủ tồn kho
        - Tạo stock movement
        - Cập nhật stock quantity
        - Cập nhật batch quantity (FEFO)
        """
        # Check stock availability
        stock = StockService.get_stock(db, movement.warehouse_id, movement.product_id)
        if not stock or stock.quantity < movement.quantity:
            raise ValueError(
                f"Không đủ tồn kho. Hiện tại: {stock.quantity if stock else 0}, "
                f"Cần xuất: {movement.quantity}"
            )

        # Generate movement number
        movement_number = StockMovementService.generate_movement_number(
            db, movement.movement_type
        )

        # If batch not specified, use FEFO
        if not movement.batch_id:
            batches = BatchService.get_batches_fefo(db, movement.product_id)
            if not batches:
                raise ValueError("Không tìm thấy batch khả dụng (QC passed)")
            movement.batch_id = batches[0].id  # Use first batch (FEFO)

        # Create movement
        db_movement = StockMovement(
            movement_number=movement_number,
            movement_type=MovementType(movement.movement_type),
            product_id=movement.product_id,
            batch_id=movement.batch_id,
            warehouse_id=movement.warehouse_id,
            quantity=movement.quantity,
            reference_type=movement.reference_type,
            reference_id=movement.reference_id,
            note=movement.note,
            created_by=created_by,
        )
        db.add(db_movement)

        # Update stock
        stock.quantity -= movement.quantity
        stock.updated_at = datetime.utcnow()

        # Update batch
        batch = db.query(Batch).filter(Batch.id == movement.batch_id).first()
        if batch:
            batch.current_quantity -= movement.quantity
            batch.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(db_movement)

        return db_movement

    @staticmethod
    def get_movements(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        movement_type: Optional[str] = None,
        product_id: Optional[int] = None,
        warehouse_id: Optional[int] = None,
    ) -> Tuple[List[StockMovement], int]:
        """Lấy danh sách movements"""
        query = db.query(StockMovement)

        if movement_type:
            query = query.filter(StockMovement.movement_type == movement_type)
        if product_id:
            query = query.filter(StockMovement.product_id == product_id)
        if warehouse_id:
            query = query.filter(StockMovement.warehouse_id == warehouse_id)

        total = query.count()
        movements = (
            query.order_by(StockMovement.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return movements, total
