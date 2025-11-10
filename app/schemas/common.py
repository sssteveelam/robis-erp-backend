from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List

# Type variable cho generic pagination
T = TypeVar("T")


class PaginationParams(BaseModel):
    """Query parameters cho pagination"""

    page: int = Field(default=1, ge=1, description="Page number (starts from 1)")
    page_size: int = Field(
        default=10, ge=1, le=100, description="Items per page (max 100)"
    )

    @property
    def skip(self) -> int:
        """Calculate offset from page number"""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Alias for page_size"""
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""

    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(
        cls, items: List[T], total: int, page: int, page_size: int
    ) -> "PaginatedResponse[T]":
        """Helper method to create paginated response"""
        total_pages = (total + page_size - 1) // page_size  # Ceiling division

        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
