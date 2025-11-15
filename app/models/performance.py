from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Date,
    Time,
    DateTime,
    Text,
    Numeric,
    Boolean,
    Enum,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base


class PerformanceReview(Base):
    """Đánh giá hiệu suất nhân viên"""

    __tablename__ = "performance_reviews"

    id = Column(Integer, primary_key=True, index=True)

    # Who & When
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    reviewer_id = Column(
        Integer, ForeignKey("employees.id"), nullable=False
    )  # Manager đánh giá
    review_period = Column(String(50), nullable=False)  # "Q1-2025", "2024"
    review_date = Column(Date, nullable=False)

    # Scores
    score = Column(Numeric(3, 1), nullable=False)  # Điểm tổng thể (0-5 hoặc 0-100)
    kpi_achieved = Column(Numeric(5, 2))  # % KPI đạt được (0-100)

    # Feedback
    strengths = Column(Text)  # Điểm mạnh
    areas_for_improvement = Column(Text)  # Điểm cần cải thiện
    action_plan = Column(Text)  # Kế hoạch hành động

    # Career Development
    promotion_recommended = Column(Boolean, default=False)  # Đề xuất thăng chức
    training_recommended = Column(Text)  # Đề xuất đào tạo

    # Notes
    reviewer_note = Column(Text)
    employee_comment = Column(Text)  # Nhân viên phản hồi

    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    employee = relationship(
        "Employee",
        foreign_keys=[employee_id],
        back_populates="performance_reviews_received",
    )
    reviewer = relationship(
        "Employee",
        foreign_keys=[reviewer_id],
        back_populates="performance_reviews_given",
    )
