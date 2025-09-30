"""Base repository with common CRUD operations."""
from typing import Generic, TypeVar, Type, Optional, List, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload

from ..database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository class with common CRUD operations."""

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        obj = self.model(**kwargs)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get_by_id(self, obj_id: UUID) -> Optional[ModelType]:
        """Get record by ID."""
        query = select(self.model).where(self.model.id == obj_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination."""
        query = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, obj_id: UUID, **kwargs) -> Optional[ModelType]:
        """Update record by ID."""
        query = (
            update(self.model)
            .where(self.model.id == obj_id)
            .values(**kwargs)
            .returning(self.model)
        )
        result = await self.db.execute(query)
        await self.db.commit()
        return result.scalar_one_or_none()

    async def delete(self, obj_id: UUID) -> bool:
        """Delete record by ID."""
        query = delete(self.model).where(self.model.id == obj_id)
        result = await self.db.execute(query)
        await self.db.commit()
        return result.rowcount > 0

    async def count(self) -> int:
        """Count total records."""
        query = select(func.count(self.model.id))
        result = await self.db.execute(query)
        return result.scalar() or 0