"""
Database connection for scraper service.
"""
import asyncpg
from contextlib import asynccontextmanager
from typing import Dict, Any, List
from config import settings


async def init_db():
    """Initialize database connection."""
    pass  # Database is already initialized by main app


@asynccontextmanager
async def get_db_session():
    """Get database session."""
    conn = await asyncpg.connect(settings.database_url)
    try:
        yield conn
    finally:
        await conn.close()


async def save_hackathon(hackathon_data: Dict[str, Any]) -> bool:
    """Save hackathon to database."""
    async with get_db_session() as conn:
        try:
            # Check if hackathon already exists
            existing = await conn.fetchrow(
                """
                SELECT id FROM hackathons
                WHERE source_platform = $1 AND source_id = $2
                """,
                hackathon_data.get("source_platform"),
                hackathon_data.get("source_id")
            )

            if existing:
                # Update existing hackathon
                await conn.execute(
                    """
                    UPDATE hackathons SET
                        title = $3, description = $4, website_url = $5,
                        start_date = $6, end_date = $7, location = $8,
                        updated_at = NOW(), scraped_at = NOW()
                    WHERE source_platform = $1 AND source_id = $2
                    """,
                    hackathon_data.get("source_platform"),
                    hackathon_data.get("source_id"),
                    hackathon_data.get("title"),
                    hackathon_data.get("description"),
                    hackathon_data.get("website_url"),
                    hackathon_data.get("start_date"),
                    hackathon_data.get("end_date"),
                    hackathon_data.get("location")
                )
                return False  # Updated existing
            else:
                # Insert new hackathon
                await conn.execute(
                    """
                    INSERT INTO hackathons (
                        title, description, website_url, registration_url,
                        start_date, end_date, location, is_online,
                        prize_money, categories, technologies,
                        source_platform, source_id, source_url,
                        scraped_at, created_at, updated_at
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14,
                        NOW(), NOW(), NOW()
                    )
                    """,
                    hackathon_data.get("title"),
                    hackathon_data.get("description"),
                    hackathon_data.get("website_url"),
                    hackathon_data.get("registration_url"),
                    hackathon_data.get("start_date"),
                    hackathon_data.get("end_date"),
                    hackathon_data.get("location"),
                    hackathon_data.get("is_online", False),
                    hackathon_data.get("prize_money"),
                    hackathon_data.get("categories", []),
                    hackathon_data.get("technologies", []),
                    hackathon_data.get("source_platform"),
                    hackathon_data.get("source_id"),
                    hackathon_data.get("source_url")
                )
                return True  # New hackathon

        except Exception as e:
            print(f"Error saving hackathon: {e}")
            return False


async def save_scraping_job(
    platform: str,
    status: str,
    hackathons_scraped: int = 0,
    errors_encountered: int = 0,
    error_details: Dict = None
):
    """Save scraping job result."""
    async with get_db_session() as conn:
        await conn.execute(
            """
            INSERT INTO scraping_jobs (
                platform, status, hackathons_scraped, errors_encountered,
                error_details, started_at, completed_at, created_at
            ) VALUES ($1, $2, $3, $4, $5, NOW(), NOW(), NOW())
            """,
            platform, status, hackathons_scraped, errors_encountered, error_details or {}
        )