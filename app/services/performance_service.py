"""
Performance Review Service
"""

from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date

from app.models.performance import PerformanceReview  # ← SAI - PerformanceReview ở đây
from app.models.hr import Employee
from app.schemas.performance import (
    PerformanceReviewCreate,
    PerformanceReviewUpdate,
    PerformanceReviewWithDetails,
)


class PerformanceService:

    @staticmethod
    def create_review(
        db: Session, review: PerformanceReviewCreate, reviewer_id: int
    ) -> PerformanceReview:
        """Tạo performance review mới"""

        # Validate reviewer có phải manager của employee không
        employee = db.query(Employee).filter(Employee.id == review.employee_id).first()
        if not employee:
            raise ValueError("Employee không tồn tại")

        # Optional: Check reviewer is manager
        # if employee.direct_manager_id != reviewer_id:
        #     raise ValueError("Chỉ direct manager mới có thể đánh giá")

        db_review = PerformanceReview(**review.dict(), reviewer_id=reviewer_id)

        db.add(db_review)
        db.commit()
        db.refresh(db_review)
        return db_review

    @staticmethod
    def get_reviews(
        db: Session,
        employee_id: Optional[int] = None,
        reviewer_id: Optional[int] = None,
        review_period: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[PerformanceReview], int]:
        """Lấy danh sách performance reviews"""
        query = db.query(PerformanceReview)

        if employee_id:
            query = query.filter(PerformanceReview.employee_id == employee_id)
        if reviewer_id:
            query = query.filter(PerformanceReview.reviewer_id == reviewer_id)
        if review_period:
            query = query.filter(PerformanceReview.review_period == review_period)

        total = query.count()
        reviews = (
            query.order_by(PerformanceReview.review_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return reviews, total

    @staticmethod
    def get_review_by_id(db: Session, review_id: int) -> Optional[PerformanceReview]:
        """Lấy review theo ID"""
        return (
            db.query(PerformanceReview)
            .filter(PerformanceReview.id == review_id)
            .first()
        )

    @staticmethod
    def update_review(
        db: Session, review_id: int, review_update: PerformanceReviewUpdate
    ) -> Optional[PerformanceReview]:
        """Cập nhật performance review"""
        db_review = (
            db.query(PerformanceReview)
            .filter(PerformanceReview.id == review_id)
            .first()
        )

        if not db_review:
            return None

        update_data = review_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_review, key, value)

        db.commit()
        db.refresh(db_review)
        return db_review

    @staticmethod
    def get_employee_review_history(
        db: Session, employee_id: int
    ) -> List[PerformanceReviewWithDetails]:
        """Lấy lịch sử đánh giá của employee"""
        reviews = (
            db.query(PerformanceReview)
            .filter(PerformanceReview.employee_id == employee_id)
            .order_by(PerformanceReview.review_date.desc())
            .all()
        )

        # Attach employee & reviewer names
        result = []
        for review in reviews:
            employee = (
                db.query(Employee).filter(Employee.id == review.employee_id).first()
            )
            reviewer = (
                db.query(Employee).filter(Employee.id == review.reviewer_id).first()
            )

            review_dict = {
                **review.__dict__,
                "employee_name": employee.full_name if employee else None,
                "reviewer_name": reviewer.full_name if reviewer else None,
            }
            result.append(PerformanceReviewWithDetails(**review_dict))

        return result

    @staticmethod
    def get_promotion_candidates(
        db: Session, min_score: float = 80.0
    ) -> List[Employee]:
        """
        Lấy danh sách nhân viên đề xuất thăng chức
        Criteria: avg_score >= min_score hoặc promotion_recommended = True
        """
        # Subquery: Get latest review for each employee
        from sqlalchemy import func

        latest_reviews = (
            db.query(
                PerformanceReview.employee_id,
                func.max(PerformanceReview.review_date).label("latest_date"),
            )
            .group_by(PerformanceReview.employee_id)
            .subquery()
        )

        # Get employees with high scores or promotion recommended
        reviews = (
            db.query(PerformanceReview)
            .join(
                latest_reviews,
                (PerformanceReview.employee_id == latest_reviews.c.employee_id)
                & (PerformanceReview.review_date == latest_reviews.c.latest_date),
            )
            .filter(
                (PerformanceReview.score >= min_score)
                | (PerformanceReview.promotion_recommended == True)
            )
            .all()
        )

        # Get employee details
        employee_ids = [r.employee_id for r in reviews]
        employees = db.query(Employee).filter(Employee.id.in_(employee_ids)).all()

        return employees

    @staticmethod
    def get_average_score(db: Session, employee_id: int) -> Optional[float]:
        """Tính điểm trung bình của employee"""
        from sqlalchemy import func

        avg_score = (
            db.query(func.avg(PerformanceReview.score))
            .filter(PerformanceReview.employee_id == employee_id)
            .scalar()
        )

        return float(avg_score) if avg_score else None
