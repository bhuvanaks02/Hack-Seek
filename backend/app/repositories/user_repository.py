"""User repository for database operations."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .base import BaseRepository
from ..models.user import User


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        email: str,
        password_hash: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """Create a new user."""
        return await self.create(
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name
        )

    async def update_user(self, user_id, **kwargs) -> Optional[User]:
        """Update user information."""
        # Remove password_hash from kwargs if it's None to avoid clearing it
        if 'password_hash' in kwargs and kwargs['password_hash'] is None:
            del kwargs['password_hash']
        return await self.update(user_id, **kwargs)

    async def activate_user(self, user_id) -> Optional[User]:
        """Activate user account."""
        return await self.update(user_id, is_active=True)

    async def verify_user(self, user_id) -> Optional[User]:
        """Verify user email."""
        return await self.update(user_id, is_verified=True)