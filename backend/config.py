"""
Configuration settings for the Hack-Seek backend application.
"""
import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings configuration."""

    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "postgresql://hackseek_user:password@localhost:5432/hackseek_db")
    database_host: str = os.getenv("DATABASE_HOST", "localhost")
    database_port: int = int(os.getenv("DATABASE_PORT", "5432"))
    database_name: str = os.getenv("DATABASE_NAME", "hackseek_db")
    database_user: str = os.getenv("DATABASE_USER", "hackseek_user")
    database_password: str = os.getenv("DATABASE_PASSWORD", "password")

    # AI API Configuration
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
    claude_api_key: Optional[str] = os.getenv("CLAUDE_API_KEY")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    ollama_endpoint: str = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")

    # Social Media APIs
    twitter_bearer_token: Optional[str] = os.getenv("TWITTER_BEARER_TOKEN")

    # Application Configuration
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    api_base_url: str = os.getenv("API_BASE_URL", "http://localhost:8000")
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Security
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "jwt-secret-change-in-production")
    jwt_expiration_hours: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")

    # Rate Limiting
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

    # Scraping Configuration
    scraping_delay: int = int(os.getenv("SCRAPING_DELAY", "1"))
    max_concurrent_scrapers: int = int(os.getenv("MAX_CONCURRENT_SCRAPERS", "5"))
    user_agent: str = os.getenv("USER_AGENT", "HackSeek-Bot/1.0")

    # Redis Configuration
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Email Configuration
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: Optional[str] = os.getenv("SMTP_USER")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()