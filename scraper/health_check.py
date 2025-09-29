"""
Health check script for the HackSeek scraper service.
"""
import asyncio
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any

import asyncpg
import redis
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Scraper settings."""
    database_url: str = "postgresql://hackseek_user:password@localhost:5432/hackseek_db"
    redis_url: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"


async def check_database_health() -> Dict[str, Any]:
    """Check database connectivity and health."""
    start_time = time.time()
    try:
        settings = Settings()
        conn = await asyncpg.connect(settings.database_url)

        # Test basic query
        result = await conn.fetchval("SELECT 1")
        await conn.close()

        response_time = (time.time() - start_time) * 1000

        return {
            "status": "healthy",
            "type": "postgresql",
            "response_time_ms": round(response_time, 2),
            "test_query_result": result
        }
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return {
            "status": "unhealthy",
            "type": "postgresql",
            "response_time_ms": round(response_time, 2),
            "error": str(e)
        }


def check_redis_health() -> Dict[str, Any]:
    """Check Redis connectivity and health."""
    start_time = time.time()
    try:
        settings = Settings()
        r = redis.from_url(settings.redis_url)

        # Test basic operations
        r.ping()
        test_key = "health_check_test"
        r.set(test_key, "test_value", ex=60)
        result = r.get(test_key)
        r.delete(test_key)

        response_time = (time.time() - start_time) * 1000

        return {
            "status": "healthy",
            "type": "redis",
            "response_time_ms": round(response_time, 2),
            "test_operation": "success"
        }
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        return {
            "status": "unhealthy",
            "type": "redis",
            "response_time_ms": round(response_time, 2),
            "error": str(e)
        }


def check_scraper_dependencies() -> Dict[str, Any]:
    """Check scraper dependencies."""
    dependencies = {}

    # Check Scrapy
    try:
        import scrapy
        dependencies["scrapy"] = {
            "status": "available",
            "version": scrapy.__version__
        }
    except ImportError as e:
        dependencies["scrapy"] = {
            "status": "unavailable",
            "error": str(e)
        }

    # Check BeautifulSoup
    try:
        import bs4
        dependencies["beautifulsoup4"] = {
            "status": "available",
            "version": bs4.__version__
        }
    except ImportError as e:
        dependencies["beautifulsoup4"] = {
            "status": "unavailable",
            "error": str(e)
        }

    # Check Selenium
    try:
        import selenium
        dependencies["selenium"] = {
            "status": "available",
            "version": selenium.__version__
        }
    except ImportError as e:
        dependencies["selenium"] = {
            "status": "unavailable",
            "error": str(e)
        }

    # Check requests
    try:
        import requests
        dependencies["requests"] = {
            "status": "available",
            "version": requests.__version__
        }
    except ImportError as e:
        dependencies["requests"] = {
            "status": "unavailable",
            "error": str(e)
        }

    return dependencies


async def run_health_check() -> Dict[str, Any]:
    """Run comprehensive health check."""
    start_time = time.time()

    health_data = {
        "status": "healthy",
        "service": "scraper",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {},
        "dependencies": {},
        "response_time_ms": 0
    }

    # Check database
    health_data["services"]["database"] = await check_database_health()

    # Check Redis
    health_data["services"]["redis"] = check_redis_health()

    # Check dependencies
    health_data["dependencies"] = check_scraper_dependencies()

    # Calculate overall health
    unhealthy_services = []
    for name, service in health_data["services"].items():
        if service.get("status") != "healthy":
            unhealthy_services.append(name)

    unavailable_deps = []
    for name, dep in health_data["dependencies"].items():
        if dep.get("status") != "available":
            unavailable_deps.append(name)

    if unhealthy_services or unavailable_deps:
        health_data["status"] = "degraded" if not unhealthy_services else "unhealthy"
        if unhealthy_services:
            health_data["unhealthy_services"] = unhealthy_services
        if unavailable_deps:
            health_data["unavailable_dependencies"] = unavailable_deps

    # Calculate response time
    health_data["response_time_ms"] = round((time.time() - start_time) * 1000, 2)

    return health_data


async def main():
    """Main health check function."""
    try:
        health_result = await run_health_check()

        # Print JSON result
        print(json.dumps(health_result, indent=2))

        # Exit with appropriate code
        if health_result["status"] == "healthy":
            sys.exit(0)
        elif health_result["status"] == "degraded":
            sys.exit(1)
        else:
            sys.exit(2)

    except Exception as e:
        error_result = {
            "status": "error",
            "service": "scraper",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())