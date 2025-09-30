"""Hackathon repository for database operations."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc

from .base import BaseRepository
from ..models.hackathon import Hackathon


class HackathonRepository(BaseRepository[Hackathon]):
    """Repository for Hackathon model operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Hackathon, db)

    async def get_active_hackathons(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Hackathon]:
        """Get active hackathons."""
        query = (
            select(Hackathon)
            .where(Hackathon.is_active == True)
            .order_by(desc(Hackathon.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_upcoming_hackathons(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Hackathon]:
        """Get upcoming hackathons."""
        now = datetime.utcnow()
        query = (
            select(Hackathon)
            .where(
                and_(
                    Hackathon.is_active == True,
                    Hackathon.start_date > now
                )
            )
            .order_by(asc(Hackathon.start_date))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def search_hackathons(
        self,
        query_text: Optional[str] = None,
        location: Optional[str] = None,
        categories: Optional[List[str]] = None,
        technologies: Optional[List[str]] = None,
        is_online: Optional[bool] = None,
        min_prize: Optional[float] = None,
        difficulty_level: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Hackathon]:
        """Search hackathons with filters."""
        query = select(Hackathon).where(Hackathon.is_active == True)

        # Text search
        if query_text:
            search_filter = or_(
                Hackathon.title.ilike(f"%{query_text}%"),
                Hackathon.description.ilike(f"%{query_text}%"),
                Hackathon.organizer.ilike(f"%{query_text}%")
            )
            query = query.where(search_filter)

        # Location filter
        if location:
            query = query.where(Hackathon.location.ilike(f"%{location}%"))

        # Category filter
        if categories:
            query = query.where(Hackathon.categories.overlap(categories))

        # Technology filter
        if technologies:
            query = query.where(Hackathon.technologies.overlap(technologies))

        # Online filter
        if is_online is not None:
            query = query.where(Hackathon.is_online == is_online)

        # Prize filter
        if min_prize is not None:
            query = query.where(Hackathon.prize_money >= min_prize)

        # Difficulty filter
        if difficulty_level:
            query = query.where(Hackathon.difficulty_level == difficulty_level)

        # Order and pagination
        query = query.order_by(desc(Hackathon.start_date)).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_source(
        self,
        source_platform: str,
        source_id: str
    ) -> Optional[Hackathon]:
        """Get hackathon by source platform and ID."""
        query = select(Hackathon).where(
            and_(
                Hackathon.source_platform == source_platform,
                Hackathon.source_id == source_id
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_hackathon(self, hackathon_data: Dict[str, Any]) -> Hackathon:
        """Create a new hackathon."""
        return await self.create(**hackathon_data)

    async def update_hackathon(
        self,
        hackathon_id: UUID,
        hackathon_data: Dict[str, Any]
    ) -> Optional[Hackathon]:
        """Update hackathon information."""
        return await self.update(hackathon_id, **hackathon_data)

    async def get_featured_hackathons(
        self,
        limit: int = 10
    ) -> List[Hackathon]:
        """Get featured hackathons with highest prize money."""
        query = (
            select(Hackathon)
            .where(
                and_(
                    Hackathon.is_active == True,
                    Hackathon.prize_money.isnot(None),
                    Hackathon.prize_money > 0
                )
            )
            .order_by(desc(Hackathon.prize_money))
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())