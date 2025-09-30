"""Hackathon model."""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import Boolean, String, Text, DateTime, Integer, Numeric, func, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Hackathon(Base):
    __tablename__ = "hackathons"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    short_description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    organizer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    registration_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Dates
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    registration_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    # Location and format
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_hybrid: Mapped[bool] = mapped_column(Boolean, default=False)

    # Participation details
    participation_fee: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), default=0)
    prize_money: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    max_participants: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    difficulty_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)

    # Categories and technologies as arrays
    categories: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    technologies: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)

    # Source tracking
    source_platform: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    source_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    scraped_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    favorites = relationship("UserFavorite", back_populates="hackathon", cascade="all, delete-orphan")

    @property
    def is_upcoming(self) -> bool:
        """Check if hackathon is upcoming."""
        if not self.start_date:
            return False
        return self.start_date > datetime.utcnow()

    @property
    def is_registration_open(self) -> bool:
        """Check if registration is still open."""
        if not self.registration_deadline:
            return True
        return self.registration_deadline > datetime.utcnow()

    def __repr__(self):
        return f"<Hackathon {self.title}>"


# Add indexes for better query performance
Index('ix_hackathons_categories', Hackathon.categories, postgresql_using='gin')
Index('ix_hackathons_technologies', Hackathon.technologies, postgresql_using='gin')
Index('ix_hackathons_source_unique', Hackathon.source_platform, Hackathon.source_id, unique=True)