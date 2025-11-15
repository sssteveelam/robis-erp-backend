"""
Performance Review API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.schemas.performance import (
    PerformanceReview,
    PerformanceReviewCreate,
    PerformanceReviewUpdate,
    PerformanceReviewWithDetails,
)
from app.schemas.hr import Employee
from app.schemas.common import PaginatedResponse
from app.services.performance_service import PerformanceService
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.permissions import require_permission
from app.models.user import User as UserModel

router = APIRouter(tags=["Performance Reviews"])


@router.post(
    "/performance-reviews",
    response_model=PerformanceReview,
    status_code=status.HTTP_201_CREATED,
    dependencies=[require_permission("hr:evaluate")],
)
def create_performance_review(
    review: PerformanceReviewCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Tạo performance review mới

    Permission: hr:evaluate
    Roles: HR_STAFF, Managers
    """
    try:
        # reviewer_id = current_user.id (nếu có employee record)
        # Tạm thời dùng reviewer_id từ request
        return PerformanceService.create_review(db, review, review.reviewer_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/performance-reviews",
    response_model=PaginatedResponse[PerformanceReview],
    dependencies=[require_permission("hr:read")],
)
def get_performance_reviews(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    employee_id: Optional[int] = Query(default=None),
    reviewer_id: Optional[int] = Query(default=None),
    review_period: Optional[str] = Query(default=None, description="VD: Q1-2025, 2024"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Lấy danh sách performance reviews"""
    skip = (page - 1) * page_size

    reviews, total = PerformanceService.get_reviews(
        db=db,
        skip=skip,
        limit=page_size,
        employee_id=employee_id,
        reviewer_id=reviewer_id,
        review_period=review_period,
    )

    return PaginatedResponse.create(
        items=reviews, total=total, page=page, page_size=page_size
    )


@router.get(
    "/performance-reviews/{review_id}",
    response_model=PerformanceReview,
    dependencies=[require_permission("hr:read")],
)
def get_performance_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Lấy performance review theo ID"""
    review = PerformanceService.get_review_by_id(db, review_id)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Performance review với ID {review_id} không tồn tại",
        )

    return review


@router.put(
    "/performance-reviews/{review_id}",
    response_model=PerformanceReview,
    dependencies=[require_permission("hr:evaluate")],
)
def update_performance_review(
    review_id: int,
    review_update: PerformanceReviewUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Cập nhật performance review"""
    review = PerformanceService.update_review(db, review_id, review_update)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Performance review với ID {review_id} không tồn tại",
        )

    return review


@router.get(
    "/performance-reviews/employee/{employee_id}/history",
    response_model=list[PerformanceReviewWithDetails],
    dependencies=[require_permission("hr:read")],
)
def get_employee_review_history(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Lấy lịch sử đánh giá của employee

    Trả về tất cả performance reviews kèm employee & reviewer names
    """
    return PerformanceService.get_employee_review_history(db, employee_id)


@router.get(
    "/performance-reviews/promotion-candidates",
    response_model=list[Employee],
    dependencies=[require_permission("hr:read")],
)
def get_promotion_candidates(
    min_score: float = Query(default=80.0, ge=0, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """
    Lấy danh sách nhân viên đề xuất thăng chức

    Criteria:
    - Average score >= min_score
    - Hoặc promotion_recommended = True
    """
    return PerformanceService.get_promotion_candidates(db, min_score)


@router.get(
    "/performance-reviews/employee/{employee_id}/average-score",
    dependencies=[require_permission("hr:read")],
)
def get_employee_average_score(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Lấy điểm trung bình của employee"""
    avg_score = PerformanceService.get_average_score(db, employee_id)

    if avg_score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee chưa có performance review nào",
        )

    return {"employee_id": employee_id, "average_score": avg_score}
