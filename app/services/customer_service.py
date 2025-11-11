"""
Customer Service - Business Logic cho Customer
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, Tuple, List
from datetime import datetime

from app.models.customer import Customer, CustomerType
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:

    @staticmethod
    def generate_customer_code(db: Session, customer_type: str) -> str:
        """
        Generate unique customer code
        Format: B2C-YYYYMMDD-XXX hoặc B2B-YYYYMMDD-XXX
        """
        prefix = customer_type.upper()
        today = datetime.now().strftime("%Y%m%d")

        # Đếm số customer cùng loại được tạo hôm nay
        count = (
            db.query(Customer)
            .filter(Customer.customer_code.like(f"{prefix}-{today}-%"))
            .count()
        )

        sequence = str(count + 1).zfill(3)
        return f"{prefix}-{today}-{sequence}"

    @staticmethod
    def create_customer(db: Session, customer: CustomerCreate) -> Customer:
        """Tạo customer mới"""

        # Generate customer code
        customer_code = CustomerService.generate_customer_code(
            db, customer.customer_type
        )

        # Create customer
        db_customer = Customer(
            customer_code=customer_code,
            customer_type=CustomerType(customer.customer_type),
            name=customer.name,
            email=customer.email,
            phone=customer.phone,
            company_name=customer.company_name,
            tax_code=customer.tax_code,
            address=customer.address,
            city=customer.city,
            district=customer.district,
            is_active=True,
        )

        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)

        return db_customer

    @staticmethod
    def get_customers(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        customer_type: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[Customer], int]:
        """
        Lấy danh sách customers với filter và pagination
        Returns: (customers, total_count)
        """
        query = db.query(Customer)

        # Filter by search
        if search:
            query = query.filter(
                or_(
                    Customer.name.ilike(f"%{search}%"),
                    Customer.customer_code.ilike(f"%{search}%"),
                    Customer.email.ilike(f"%{search}%"),
                    Customer.phone.ilike(f"%{search}%"),
                )
            )

        # Filter by customer_type
        if customer_type:
            query = query.filter(Customer.customer_type == customer_type)

        # Filter by is_active
        if is_active is not None:
            query = query.filter(Customer.is_active == is_active)

        # Get total count
        total = query.count()

        # Apply pagination
        customers = (
            query.order_by(Customer.created_at.desc()).offset(skip).limit(limit).all()
        )

        return customers, total

    @staticmethod
    def get_customer_by_id(db: Session, customer_id: int) -> Optional[Customer]:
        """Lấy customer theo ID"""
        return db.query(Customer).filter(Customer.id == customer_id).first()

    @staticmethod
    def update_customer(
        db: Session, customer_id: int, customer_update: CustomerUpdate
    ) -> Optional[Customer]:
        """Update customer"""
        db_customer = CustomerService.get_customer_by_id(db, customer_id)

        if not db_customer:
            return None

        # Update fields
        update_data = customer_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_customer, field, value)

        db_customer.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_customer)

        return db_customer

    @staticmethod
    def delete_customer(db: Session, customer_id: int) -> bool:
        """Soft delete customer"""
        db_customer = CustomerService.get_customer_by_id(db, customer_id)

        if not db_customer:
            return False

        db_customer.is_active = False
        db_customer.updated_at = datetime.utcnow()
        db.commit()

        return True
