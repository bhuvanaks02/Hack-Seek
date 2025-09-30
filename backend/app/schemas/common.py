"""Common schemas used across the application."""
from typing import Generic, TypeVar, List
from pydantic import BaseModel

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema."""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        size: int
    ):
        """Create paginated response."""
        pages = (total + size - 1) // size  # Ceiling division
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str