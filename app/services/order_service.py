"""
Order Service - Business Logic cho Orders
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, Tuple, List
from datetime import datetime

from app.models.order import Order, OrderItem, OrderStatusLog, OrderStatus, OrderType
from app.schemas.order import OrderCreate, OrderUpdate, OrderStatusUpdate


class OrderService:

    @staticmethod
    def generate_order_number(db: Session, order_type: str) -> str:
        """
        Generate unique order number
        Format: ORD-B2C-YYYYMMDD-XXXX hoặc ORD-B2B-YYYYMMDD-XXXX
        """
        prefix = f"ORD-{order_type.upper()}"
        today = datetime.now().strftime("%Y%m%d")

        # Đếm số orders cùng loại được tạo hôm nay
        count = (
            db.query(Order)
            .filter(Order.order_number.like(f"{prefix}-{today}-%"))
            .count()
        )

        sequence = str(count + 1).zfill(4)
        return f"{prefix}-{today}-{sequence}"

    @staticmethod
    def calculate_order_total(order_data: OrderCreate) -> dict:
        """
        Tính toán tổng tiền đơn hàng
        Returns: {subtotal, discount_amount, tax_amount, total_amount}
        """
        subtotal = 0

        # Tính subtotal từ items
        for item in order_data.items:
            item_subtotal = item.unit_price * item.quantity
            item_discount = item_subtotal * (item.discount_percent / 100)
            subtotal += item_subtotal - item_discount

        # Discount amount
        discount_amount = order_data.discount_amount or 0

        # Tax (10% VAT)
        tax_amount = (subtotal - discount_amount) * 0.1

        # Total
        shipping_fee = order_data.shipping_fee or 0
        total_amount = subtotal - discount_amount + tax_amount + shipping_fee

        return {
            "subtotal": round(subtotal, 2),
            "discount_amount": round(discount_amount, 2),
            "tax_amount": round(tax_amount, 2),
            "shipping_fee": round(shipping_fee, 2),
            "total_amount": round(total_amount, 2),
        }

    @staticmethod
    def create_order(db: Session, order_data: OrderCreate, created_by: int) -> Order:
        """Tạo order mới"""

        # Generate order number
        order_number = OrderService.generate_order_number(db, order_data.order_type)

        # Calculate totals
        totals = OrderService.calculate_order_total(order_data)

        # Create order
        db_order = Order(
            order_number=order_number,
            order_type=OrderType(order_data.order_type),
            customer_id=order_data.customer_id,
            status=OrderStatus.DRAFT,
            subtotal=totals["subtotal"],
            discount_amount=totals["discount_amount"],
            tax_amount=totals["tax_amount"],
            shipping_fee=totals["shipping_fee"],
            total_amount=totals["total_amount"],
            payment_method=order_data.payment_method,
            payment_status="unpaid",
            paid_amount=0,
            shipping_address=order_data.shipping_address,
            shipping_city=order_data.shipping_city,
            shipping_district=order_data.shipping_district,
            shipping_note=order_data.shipping_note,
            internal_note=order_data.internal_note,
            created_by=created_by,
        )

        db.add(db_order)
        db.flush()  # Get order.id

        # Create order items
        for item_data in order_data.items:
            item_subtotal = item_data.unit_price * item_data.quantity
            item_discount = item_subtotal * (item_data.discount_percent / 100)

            db_item = OrderItem(
                order_id=db_order.id,
                product_id=item_data.product_id,
                product_name=item_data.product_name,
                product_sku=item_data.product_sku,
                unit_price=item_data.unit_price,
                quantity=item_data.quantity,
                discount_percent=item_data.discount_percent,
                discount_amount=round(item_discount, 2),
                subtotal=round(item_subtotal - item_discount, 2),
            )
            db.add(db_item)

        # Create status log
        status_log = OrderStatusLog(
            order_id=db_order.id,
            from_status=None,
            to_status=OrderStatus.DRAFT.value,
            note="Order created",
            changed_by=created_by,
        )
        db.add(status_log)

        db.commit()
        db.refresh(db_order)

        return db_order

    @staticmethod
    def get_orders(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        status: Optional[str] = None,
        order_type: Optional[str] = None,
        customer_id: Optional[int] = None,
    ) -> Tuple[List[Order], int]:
        """Lấy danh sách orders với filter"""
        query = db.query(Order)

        # Filter by search
        if search:
            query = query.filter(
                or_(
                    Order.order_number.ilike(f"%{search}%"),
                    Order.internal_note.ilike(f"%{search}%"),
                )
            )

        # Filter by status
        if status:
            query = query.filter(Order.status == status)

        # Filter by order_type
        if order_type:
            query = query.filter(Order.order_type == order_type)

        # Filter by customer_id
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)

        # Get total
        total = query.count()

        # Pagination
        orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()

        return orders, total

    @staticmethod
    def get_order_by_id(db: Session, order_id: int) -> Optional[Order]:
        """Lấy order theo ID"""
        return db.query(Order).filter(Order.id == order_id).first()

    @staticmethod
    def update_order_status(
        db: Session, order_id: int, status_update: OrderStatusUpdate, changed_by: int
    ) -> Optional[Order]:
        """Cập nhật trạng thái order"""
        db_order = OrderService.get_order_by_id(db, order_id)

        if not db_order:
            return None

        old_status = db_order.status
        new_status = status_update.status

        # Update status
        db_order.status = OrderStatus(new_status)
        db_order.updated_at = datetime.utcnow()

        # Update timestamps based on status
        if new_status == OrderStatus.CONFIRMED.value:
            db_order.confirmed_at = datetime.utcnow()
        elif new_status == OrderStatus.SHIPPED.value:
            db_order.shipped_at = datetime.utcnow()
        elif new_status == OrderStatus.DELIVERED.value:
            db_order.delivered_at = datetime.utcnow()

        # Create status log
        status_log = OrderStatusLog(
            order_id=order_id,
            from_status=old_status,
            to_status=new_status,
            note=status_update.note,
            changed_by=changed_by,
        )
        db.add(status_log)

        db.commit()
        db.refresh(db_order)

        return db_order
