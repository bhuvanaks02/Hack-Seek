"""Hackathon API endpoints."""
from uuid import UUID
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..repositories.hackathon_repository import HackathonRepository
from ..schemas.hackathon import HackathonCreate, HackathonResponse, HackathonUpdate, HackathonSearch
from ..schemas.common import PaginatedResponse
from ..services.ai_service import ai_service

router = APIRouter(prefix="/hackathons", tags=["Hackathons"])


@router.get("/", response_model=PaginatedResponse[HackathonResponse])
async def get_hackathons(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: AsyncSession = Depends(get_db)
):
    """Get all active hackathons with pagination."""
    hackathon_repo = HackathonRepository(db)

    skip = (page - 1) * size
    hackathons = await hackathon_repo.get_active_hackathons(skip=skip, limit=size)
    total = await hackathon_repo.count()

    return PaginatedResponse.create(
        items=hackathons,
        total=total,
        page=page,
        size=size
    )


@router.get("/search", response_model=PaginatedResponse[HackathonResponse])
async def search_hackathons(
    q: str = Query(None, description="Search query"),
    location: str = Query(None, description="Location filter"),
    categories: List[str] = Query(None, description="Category filters"),
    technologies: List[str] = Query(None, description="Technology filters"),
    is_online: bool = Query(None, description="Online event filter"),
    min_prize: float = Query(None, ge=0, description="Minimum prize money"),
    difficulty_level: str = Query(None, description="Difficulty level"),
    semantic: bool = Query(False, description="Use AI semantic search"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: AsyncSession = Depends(get_db)
):
    """Search hackathons with filters and optional AI semantic search."""
    hackathon_repo = HackathonRepository(db)

    skip = (page - 1) * size

    # Use AI semantic search if requested and query is provided
    if semantic and q:
        try:
            # Get all matching hackathons for AI processing
            all_hackathons = await hackathon_repo.search_hackathons(
                query_text=None,  # Get all, let AI filter
                location=location,
                categories=categories,
                technologies=technologies,
                is_online=is_online,
                min_prize=min_prize,
                difficulty_level=difficulty_level,
                skip=0,
                limit=1000  # Large limit to get comprehensive results
            )

            # Perform AI semantic search
            search_results = await ai_service.semantic_search(q, all_hackathons, limit=size*2)

            # Convert AI results back to hackathons and apply pagination
            result_ids = [result.hackathon_id for result in search_results]
            hackathons = [h for h in all_hackathons if str(h.id) in result_ids]

            # Apply manual pagination
            total = len(hackathons)
            hackathons = hackathons[skip:skip + size]

        except Exception as e:
            # Fallback to regular search if AI search fails
            hackathons = await hackathon_repo.search_hackathons(
                query_text=q,
                location=location,
                categories=categories,
                technologies=technologies,
                is_online=is_online,
                min_prize=min_prize,
                difficulty_level=difficulty_level,
                skip=skip,
                limit=size
            )
            total = len(hackathons)
    else:
        # Regular search
        hackathons = await hackathon_repo.search_hackathons(
            query_text=q,
            location=location,
            categories=categories,
            technologies=technologies,
            is_online=is_online,
            min_prize=min_prize,
            difficulty_level=difficulty_level,
            skip=skip,
            limit=size
        )
        total = len(hackathons)

    return PaginatedResponse.create(
        items=hackathons,
        total=total,
        page=page,
        size=size
    )


@router.get("/upcoming", response_model=PaginatedResponse[HackathonResponse])
async def get_upcoming_hackathons(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: AsyncSession = Depends(get_db)
):
    """Get upcoming hackathons."""
    hackathon_repo = HackathonRepository(db)

    skip = (page - 1) * size
    hackathons = await hackathon_repo.get_upcoming_hackathons(skip=skip, limit=size)
    total = len(hackathons)

    return PaginatedResponse.create(
        items=hackathons,
        total=total,
        page=page,
        size=size
    )


@router.get("/featured", response_model=List[HackathonResponse])
async def get_featured_hackathons(
    limit: int = Query(10, ge=1, le=50, description="Number of featured hackathons"),
    db: AsyncSession = Depends(get_db)
):
    """Get featured hackathons with highest prizes."""
    hackathon_repo = HackathonRepository(db)
    return await hackathon_repo.get_featured_hackathons(limit=limit)


@router.get("/ai/search", response_model=Dict[str, Any])
async def ai_search_hackathons(
    query: str = Query(..., description="Natural language search query"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
    db: AsyncSession = Depends(get_db)
):
    """AI-powered natural language search for hackathons."""
    hackathon_repo = HackathonRepository(db)

    try:
        # Process natural language query
        processed = await ai_service.process_natural_language_query(query)

        # Get hackathons based on extracted filters
        filters = processed.get("filters", {})
        all_hackathons = await hackathon_repo.search_hackathons(
            query_text=processed.get("processed_query"),
            location=filters.get("location"),
            categories=filters.get("categories"),
            technologies=filters.get("technologies"),
            is_online=filters.get("is_online"),
            min_prize=filters.get("min_prize"),
            difficulty_level=filters.get("difficulty_level"),
            skip=0,
            limit=500
        )

        # Perform semantic search
        search_results = await ai_service.semantic_search(
            processed.get("processed_query", query),
            all_hackathons,
            limit=limit
        )

        # Get hackathons with relevance scores
        result_hackathons = []
        for result in search_results:
            hackathon = next((h for h in all_hackathons if str(h.id) == result.hackathon_id), None)
            if hackathon:
                result_hackathons.append({
                    "hackathon": hackathon,
                    "relevance_score": result.relevance_score,
                    "matched_terms": result.matched_terms
                })

        return {
            "query": query,
            "processed_query": processed.get("processed_query", query),
            "extracted_filters": filters,
            "results": result_hackathons,
            "total_results": len(result_hackathons)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI search failed: {str(e)}"
        )


@router.get("/ai/recommendations", response_model=List[Dict[str, Any]])
async def get_ai_recommendations(
    user_id: str = Query(..., description="User ID for personalized recommendations"),
    limit: int = Query(5, ge=1, le=20, description="Number of recommendations"),
    db: AsyncSession = Depends(get_db)
):
    """Get AI-powered personalized hackathon recommendations."""
    from ..repositories.user_repository import UserRepository

    hackathon_repo = HackathonRepository(db)
    user_repo = UserRepository(db)

    try:
        # Get user profile
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Get active hackathons
        hackathons = await hackathon_repo.get_active_hackathons(skip=0, limit=500)

        # Get AI recommendations
        recommendations = await ai_service.get_recommendations(user, hackathons, limit=limit)

        # Format response with hackathon details
        result = []
        for rec in recommendations:
            hackathon = next((h for h in hackathons if str(h.id) == rec.hackathon_id), None)
            if hackathon:
                result.append({
                    "hackathon": hackathon,
                    "recommendation_score": rec.score,
                    "reasons": rec.reasons
                })

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )


@router.get("/ai/similar/{hackathon_id}", response_model=List[HackathonResponse])
async def get_similar_hackathons(
    hackathon_id: UUID,
    limit: int = Query(5, ge=1, le=20, description="Number of similar hackathons"),
    db: AsyncSession = Depends(get_db)
):
    """Get hackathons similar to the specified one using AI."""
    hackathon_repo = HackathonRepository(db)

    try:
        # Get the reference hackathon
        reference_hackathon = await hackathon_repo.get_by_id(hackathon_id)
        if not reference_hackathon:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hackathon not found"
            )

        # Get all other hackathons
        all_hackathons = await hackathon_repo.get_active_hackathons(skip=0, limit=500)
        other_hackathons = [h for h in all_hackathons if h.id != hackathon_id]

        # Create a search query from the reference hackathon
        search_query = f"{reference_hackathon.title} {' '.join(reference_hackathon.categories or [])} {' '.join(reference_hackathon.technologies or [])}"

        # Find similar hackathons
        search_results = await ai_service.semantic_search(
            search_query,
            other_hackathons,
            limit=limit
        )

        # Return similar hackathons
        similar_hackathons = []
        for result in search_results:
            hackathon = next((h for h in other_hackathons if str(h.id) == result.hackathon_id), None)
            if hackathon:
                similar_hackathons.append(hackathon)

        return similar_hackathons

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find similar hackathons: {str(e)}"
        )


@router.get("/{hackathon_id}", response_model=HackathonResponse)
async def get_hackathon(
    hackathon_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get hackathon by ID."""
    hackathon_repo = HackathonRepository(db)
    hackathon = await hackathon_repo.get_by_id(hackathon_id)

    if not hackathon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )

    return hackathon


@router.post("/", response_model=HackathonResponse, status_code=status.HTTP_201_CREATED)
async def create_hackathon(
    hackathon_data: HackathonCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new hackathon."""
    hackathon_repo = HackathonRepository(db)

    # Check for duplicate by source
    if hackathon_data.source_platform and hackathon_data.source_id:
        existing = await hackathon_repo.get_by_source(
            hackathon_data.source_platform,
            hackathon_data.source_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Hackathon already exists from this source"
            )

    hackathon = await hackathon_repo.create_hackathon(hackathon_data.dict())
    return hackathon


@router.put("/{hackathon_id}", response_model=HackathonResponse)
async def update_hackathon(
    hackathon_id: UUID,
    hackathon_data: HackathonUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update hackathon by ID."""
    hackathon_repo = HackathonRepository(db)

    # Check if hackathon exists
    existing = await hackathon_repo.get_by_id(hackathon_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )

    # Update hackathon
    update_data = hackathon_data.dict(exclude_unset=True)
    updated_hackathon = await hackathon_repo.update_hackathon(hackathon_id, update_data)

    return updated_hackathon


@router.delete("/{hackathon_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hackathon(
    hackathon_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete hackathon by ID."""
    hackathon_repo = HackathonRepository(db)

    success = await hackathon_repo.delete(hackathon_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hackathon not found"
        )