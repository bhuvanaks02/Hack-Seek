"""Hackathon schemas for request/response validation."""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, HttpUrl, Field


class HackathonBase(BaseModel):
    """Base hackathon schema."""
    title: str = Field(..., max_length=500)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=1000)
    organizer: Optional[str] = Field(None, max_length=255)
    website_url: Optional[HttpUrl] = None
    registration_url: Optional[HttpUrl] = None
    image_url: Optional[HttpUrl] = None


class HackathonCreate(HackathonBase):
    """Schema for creating a hackathon."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    registration_deadline: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=255)
    is_online: bool = False
    is_hybrid: bool = False
    participation_fee: Optional[Decimal] = Field(None, ge=0)
    prize_money: Optional[Decimal] = Field(None, ge=0)
    max_participants: Optional[int] = Field(None, ge=1)
    difficulty_level: Optional[str] = Field(None, regex="^(Beginner|Intermediate|Advanced|All)$")
    categories: Optional[List[str]] = None
    technologies: Optional[List[str]] = None
    source_platform: Optional[str] = None
    source_id: Optional[str] = None
    source_url: Optional[HttpUrl] = None


class HackathonUpdate(BaseModel):
    """Schema for updating a hackathon."""
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=1000)
    organizer: Optional[str] = Field(None, max_length=255)
    website_url: Optional[HttpUrl] = None
    registration_url: Optional[HttpUrl] = None
    image_url: Optional[HttpUrl] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    registration_deadline: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=255)
    is_online: Optional[bool] = None
    is_hybrid: Optional[bool] = None
    participation_fee: Optional[Decimal] = Field(None, ge=0)
    prize_money: Optional[Decimal] = Field(None, ge=0)
    max_participants: Optional[int] = Field(None, ge=1)
    difficulty_level: Optional[str] = Field(None, regex="^(Beginner|Intermediate|Advanced|All)$")
    categories: Optional[List[str]] = None
    technologies: Optional[List[str]] = None
    is_active: Optional[bool] = None


class HackathonResponse(HackathonBase):
    """Schema for hackathon response."""
    id: UUID
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    registration_deadline: Optional[datetime]
    location: Optional[str]
    is_online: bool
    is_hybrid: bool
    participation_fee: Optional[Decimal]
    prize_money: Optional[Decimal]
    max_participants: Optional[int]
    difficulty_level: Optional[str]
    categories: Optional[List[str]]
    technologies: Optional[List[str]]
    source_platform: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HackathonSearch(BaseModel):
    """Schema for hackathon search parameters."""
    q: Optional[str] = Field(None, description="Search query")
    location: Optional[str] = Field(None, description="Location filter")
    categories: Optional[List[str]] = Field(None, description="Category filters")
    technologies: Optional[List[str]] = Field(None, description="Technology filters")
    is_online: Optional[bool] = Field(None, description="Online event filter")
    min_prize: Optional[float] = Field(None, ge=0, description="Minimum prize money")
    difficulty_level: Optional[str] = Field(None, regex="^(Beginner|Intermediate|Advanced|All)$")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")