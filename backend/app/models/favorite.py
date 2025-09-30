"""User favorite model."""
import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, func, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class UserFavorite(Base):
    __tablename__ = "user_favorites"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    hackathon_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("hackathons.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="favorites")
    hackathon = relationship("Hackathon", back_populates="favorites")

    def __repr__(self):
        return f"<UserFavorite user={self.user_id} hackathon={self.hackathon_id}>"


# Unique constraint to prevent duplicate favorites
Index('ix_user_favorites_unique', UserFavorite.user_id, UserFavorite.hackathon_id, unique=True)