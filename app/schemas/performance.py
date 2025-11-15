"""
Performance Review Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class PerformanceReviewBase(BaseModel):
    employee_id: int
    review_period: str = Field(..., max_length=50)  # "Q1-2025", "2024"
    review_date: date
    score: float = Field(..., ge=0, le=100)
    kpi_achieved: Optional[float] = Field(None, ge=0, le=100)
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    action_plan: Optional[str] = None
    promotion_recommended: bool = False
    training_recommended: Optional[str] = None
    reviewer_note: Optional[str] = None


class PerformanceReviewCreate(PerformanceReviewBase):
    reviewer_id: int


class PerformanceReviewUpdate(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=100)
    kpi_achieved: Optional[float] = Field(None, ge=0, le=100)
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    action_plan: Optional[str] = None
    promotion_recommended: Optional[bool] = None
    training_recommended: Optional[str] = None
    reviewer_note: Optional[str] = None
    employee_comment: Optional[str] = None


class PerformanceReview(PerformanceReviewBase):
    id: int
    reviewer_id: int
    employee_comment: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PerformanceReviewWithDetails(PerformanceReview):
    """Performance review với employee & reviewer info"""

    employee_name: Optional[str] = None
    reviewer_name: Optional[str] = None
