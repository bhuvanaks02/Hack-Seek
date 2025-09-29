"""
Main FastAPI application entry point for HackSeek.
"""
import time
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .middleware.error_handling import ErrorHandlingMiddleware, RequestLoggingMiddleware
from .utils.logger import setup_logging, get_logger

# Initialize logging
setup_logging(
    level='DEBUG' if settings.debug else 'INFO',
    enable_console=True
)
logger = get_logger('main')

# Create FastAPI application
app = FastAPI(
    title="HackSeek API",
    description="API for discovering hackathons worldwide with AI-powered assistance",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(','),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Store settings in app state
app.state.settings = settings


@app.on_event("startup")
async def startup_event():
    """Perform startup tasks."""
    logger.info("Starting HackSeek API server...")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Database URL: {settings.database_url[:50]}...")


@app.on_event("shutdown")
async def shutdown_event():
    """Perform cleanup tasks."""
    logger.info("Shutting down HackSeek API server...")


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint with basic API information."""
    return {
        "name": "HackSeek API",
        "version": "0.1.0",
        "description": "API for discovering hackathons worldwide",
        "docs_url": "/docs" if settings.debug else None,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify service status.

    Returns:
        dict: Service health status and system information
    """
    start_time = time.time()

    health_data = {
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": time.time() - app.state.start_time if hasattr(app.state, 'start_time') else 0,
        "environment": "development" if settings.debug else "production",
        "services": {}
    }

    # Check database connectivity
    try:
        # TODO: Implement actual database health check
        # For now, assume database is healthy if we can import database modules
        import asyncpg
        health_data["services"]["database"] = {
            "status": "healthy",
            "type": "postgresql",
            "response_time_ms": 0  # Placeholder
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_data["services"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # Check Redis connectivity
    try:
        # TODO: Implement actual Redis health check
        import redis
        health_data["services"]["redis"] = {
            "status": "healthy",
            "response_time_ms": 0  # Placeholder
        }
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_data["services"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }

    # Calculate overall health status
    unhealthy_services = [
        name for name, service in health_data["services"].items()
        if service.get("status") != "healthy"
    ]

    if unhealthy_services:
        health_data["status"] = "degraded"
        health_data["unhealthy_services"] = unhealthy_services

    # Calculate response time
    response_time = (time.time() - start_time) * 1000
    health_data["response_time_ms"] = round(response_time, 2)

    # Return appropriate status code
    status_code = status.HTTP_200_OK
    if health_data["status"] == "degraded":
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif health_data["status"] == "unhealthy":
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "data": health_data,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes/Docker health checks.

    Returns:
        dict: Simple ready/not ready status
    """
    # TODO: Add more comprehensive readiness checks
    # - Database connectivity
    # - Redis connectivity
    # - Required services availability

    try:
        # Basic readiness checks
        ready = True
        message = "Service is ready"

        # TODO: Implement actual readiness logic
        # For now, return ready if the application is running

        return JSONResponse(
            status_code=status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "ready": ready,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "ready": False,
                "message": f"Readiness check failed: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@app.get("/health/live", tags=["Health"])
async def liveness_check():
    """
    Liveness check endpoint for Kubernetes/Docker health checks.

    Returns:
        dict: Simple alive/dead status
    """
    # This endpoint should only fail if the application is completely broken
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "alive": True,
            "message": "Service is alive",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.get("/version", tags=["Health"])
async def version_info():
    """
    Get version and build information.

    Returns:
        dict: Version and build information
    """
    return {
        "success": True,
        "data": {
            "version": "0.1.0",
            "build": "development",
            "api_version": "v1",
            "python_version": "3.11+",
            "framework": "FastAPI",
            "timestamp": datetime.utcnow().isoformat()
        }
    }


# Store start time for uptime calculation
app.state.start_time = time.time()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )