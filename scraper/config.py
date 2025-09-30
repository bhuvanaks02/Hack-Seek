"""
Configuration settings for the scraper service.
"""
import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Scraper configuration settings."""

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://hackseek_user:password@localhost:5432/hackseek_db"
    )

    # Redis for caching and job queuing
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Scraping settings
    scraping_delay: int = int(os.getenv("SCRAPING_DELAY", "2"))
    max_concurrent_scrapers: int = int(os.getenv("MAX_CONCURRENT_SCRAPERS", "3"))
    user_agent: str = os.getenv(
        "USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))

    # Social media APIs
    twitter_bearer_token: Optional[str] = os.getenv("TWITTER_BEARER_TOKEN")

    # Debug mode
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()