"""
Monitoring and metrics middleware for FastAPI application.
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import psutil
import asyncio


class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting application metrics and monitoring."""

    def __init__(self, app, logger: logging.Logger = None):
        super().__init__(app)
        self.logger = logger or logging.getLogger(__name__)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Log request
        self.logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        # Process request
        response = await call_next(request)

        # Calculate response time
        process_time = time.time() - start_time

        # Log response
        self.logger.info(
            f"Response: {response.status_code} "
            f"for {request.method} {request.url.path} "
            f"in {process_time:.4f}s"
        )

        # Add performance headers
        response.headers["X-Process-Time"] = str(process_time)

        # Log slow requests
        if process_time > 1.0:
            self.logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {process_time:.4f}s"
            )

        return response


class HealthMetrics:
    """System health metrics collector."""

    @staticmethod
    def get_system_metrics() -> dict:
        """Get current system metrics."""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent,
                "used": psutil.virtual_memory().used
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "free": psutil.disk_usage('/').free,
                "percent": psutil.disk_usage('/').percent
            }
        }

    @staticmethod
    async def get_database_health(db_session) -> dict:
        """Check database connectivity and performance."""
        try:
            start_time = time.time()
            result = await db_session.execute("SELECT 1")
            response_time = time.time() - start_time

            return {
                "status": "healthy",
                "response_time": response_time,
                "connection_pool": "available"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time": None
            }


def setup_sentry_monitoring(dsn: str = None):
    """Configure Sentry for error monitoring."""
    if not dsn:
        return None

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

        sentry_sdk.init(
            dsn=dsn,
            integrations=[
                FastApiIntegration(auto_enabling_integrations=False),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=0.1,
            profiles_sample_rate=0.1,
            environment="production"
        )
        return sentry_sdk
    except ImportError:
        logging.warning("Sentry SDK not installed, skipping error monitoring setup")
        return None