"""
Production configuration settings for the Hack-Seek backend application.
"""
import os
from typing import Optional
from pydantic import BaseSettings


class ProductionSettings(BaseSettings):
    """Production environment settings."""

    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db:5432/hackseek_prod")
    database_pool_size: int = int(os.getenv("DATABASE_POOL_SIZE", "20"))
    database_max_overflow: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "30"))

    # Security
    secret_key: str = os.getenv("SECRET_KEY")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY")
    debug: bool = False

    # CORS Configuration
    cors_origins: str = os.getenv("CORS_ORIGINS", "https://hackseek.app,https://www.hackseek.app")

    # SSL/TLS
    ssl_redirect: bool = True
    secure_cookies: bool = True

    # Rate Limiting
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))

    # Monitoring
    sentry_dsn: Optional[str] = os.getenv("SENTRY_DSN")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Performance
    workers: int = int(os.getenv("WORKERS", "4"))
    max_connections: int = int(os.getenv("MAX_CONNECTIONS", "1000"))

    # Cache
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    cache_ttl: int = int(os.getenv("CACHE_TTL", "3600"))

    # External Services
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")

    class Config:
        env_file = ".env.production"
        case_sensitive = False


# Production settings instance
production_settings = ProductionSettings()