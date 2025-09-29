"""
Error handling middleware for the HackSeek FastAPI application.
"""
import time
import traceback
import uuid
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..utils.exceptions import (
    HackSeekException,
    create_http_exception,
    EXCEPTION_TO_HTTP_STATUS
)
from ..utils.logger import get_logger, log_exception, LogContext


logger = get_logger('middleware.error_handling')


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware to handle exceptions and format error responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and handle any exceptions."""
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # Add request ID to request state for other middleware/handlers
        request.state.request_id = request_id

        # Get client IP
        client_ip = self._get_client_ip(request)

        with LogContext(request_id=request_id, ip_address=client_ip):
            try:
                # Log incoming request
                logger.info(
                    f"Request started: {request.method} {request.url.path}",
                    extra={
                        'method': request.method,
                        'path': request.url.path,
                        'query_params': str(request.query_params),
                        'user_agent': request.headers.get('user-agent', 'Unknown')
                    }
                )

                response = await call_next(request)

                # Log successful request
                process_time = time.time() - start_time
                logger.info(
                    f"Request completed: {request.method} {request.url.path} "
                    f"[{response.status_code}] in {process_time:.3f}s"
                )

                # Add request ID to response headers
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Process-Time"] = f"{process_time:.3f}"

                return response

            except HackSeekException as exc:
                # Handle application-specific exceptions
                process_time = time.time() - start_time

                logger.warning(
                    f"Application exception: {exc.message}",
                    extra={
                        'error_code': exc.error_code,
                        'details': exc.details,
                        'process_time': process_time
                    }
                )

                return self._create_error_response(
                    request_id=request_id,
                    status_code=EXCEPTION_TO_HTTP_STATUS.get(
                        type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR
                    ),
                    error_code=exc.error_code,
                    message=exc.message,
                    details=exc.details,
                    process_time=process_time
                )

            except Exception as exc:
                # Handle unexpected exceptions
                process_time = time.time() - start_time

                log_exception(
                    logger,
                    f"Unhandled exception in request: {request.method} {request.url.path}",
                    exc_info=True,
                    extra={
                        'exception_type': type(exc).__name__,
                        'process_time': process_time
                    }
                )

                # Don't expose internal error details in production
                error_message = "An internal server error occurred"
                error_details = {}

                # In debug mode, include more details
                if hasattr(request.app.state, 'settings') and request.app.state.settings.debug:
                    error_message = str(exc)
                    error_details = {
                        'exception_type': type(exc).__name__,
                        'traceback': traceback.format_exc()
                    }

                return self._create_error_response(
                    request_id=request_id,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    error_code="INTERNAL_ERROR",
                    message=error_message,
                    details=error_details,
                    process_time=process_time
                )

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers (when behind proxy/load balancer)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()

        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip

        # Fall back to direct client IP
        if hasattr(request, 'client') and request.client:
            return request.client.host

        return 'unknown'

    def _create_error_response(
        self,
        request_id: str,
        status_code: int,
        error_code: str,
        message: str,
        details: dict,
        process_time: float
    ) -> JSONResponse:
        """Create standardized error response."""
        error_response = {
            "success": False,
            "error": {
                "code": error_code,
                "message": message,
                "details": details
            },
            "request_id": request_id,
            "timestamp": time.time()
        }

        headers = {
            "X-Request-ID": request_id,
            "X-Process-Time": f"{process_time:.3f}"
        }

        return JSONResponse(
            status_code=status_code,
            content=error_response,
            headers=headers
        )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log HTTP requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log access information."""
        start_time = time.time()

        # Get request information
        method = request.method
        path = request.url.path
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get('user-agent', 'Unknown')
        request_id = getattr(request.state, 'request_id', 'unknown')

        response = await call_next(request)

        # Calculate process time
        process_time = time.time() - start_time

        # Get user ID if available (set by auth middleware)
        user_id = getattr(request.state, 'user_id', None)

        # Log access information
        access_logger = logger.getChild('access')
        access_logger.info(
            f"{method} {path} [{response.status_code}] {process_time:.3f}s",
            extra={
                'method': method,
                'path': path,
                'status_code': response.status_code,
                'process_time': process_time,
                'client_ip': client_ip,
                'user_agent': user_agent,
                'user_id': user_id,
                'request_id': request_id
            }
        )

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()

        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip

        if hasattr(request, 'client') and request.client:
            return request.client.host

        return 'unknown'