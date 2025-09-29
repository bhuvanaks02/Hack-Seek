"""
Custom exceptions and error handling utilities for the HackSeek application.
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class HackSeekException(Exception):
    """Base exception class for HackSeek application."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(HackSeekException):
    """Raised when data validation fails."""
    pass


class AuthenticationError(HackSeekException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(HackSeekException):
    """Raised when authorization fails."""
    pass


class NotFoundError(HackSeekException):
    """Raised when a requested resource is not found."""
    pass


class DuplicateError(HackSeekException):
    """Raised when trying to create a duplicate resource."""
    pass


class DatabaseError(HackSeekException):
    """Raised when database operations fail."""
    pass


class ExternalAPIError(HackSeekException):
    """Raised when external API calls fail."""
    pass


class RateLimitError(HackSeekException):
    """Raised when rate limit is exceeded."""
    pass


class ScrapingError(HackSeekException):
    """Raised when web scraping operations fail."""
    pass


class AIServiceError(HackSeekException):
    """Raised when AI service operations fail."""
    pass


# HTTP Exception mapping
EXCEPTION_TO_HTTP_STATUS = {
    ValidationError: status.HTTP_400_BAD_REQUEST,
    AuthenticationError: status.HTTP_401_UNAUTHORIZED,
    AuthorizationError: status.HTTP_403_FORBIDDEN,
    NotFoundError: status.HTTP_404_NOT_FOUND,
    DuplicateError: status.HTTP_409_CONFLICT,
    RateLimitError: status.HTTP_429_TOO_MANY_REQUESTS,
    DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ExternalAPIError: status.HTTP_502_BAD_GATEWAY,
    ScrapingError: status.HTTP_502_BAD_GATEWAY,
    AIServiceError: status.HTTP_503_SERVICE_UNAVAILABLE,
}


def create_http_exception(
    exception: HackSeekException
) -> HTTPException:
    """Convert a HackSeek exception to an HTTP exception."""
    status_code = EXCEPTION_TO_HTTP_STATUS.get(
        type(exception),
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    detail = {
        "error": {
            "code": exception.error_code,
            "message": exception.message,
            "details": exception.details
        }
    }

    return HTTPException(status_code=status_code, detail=detail)


# Error response models for OpenAPI documentation
ERROR_RESPONSES = {
    400: {
        "description": "Bad Request",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "Invalid input data",
                        "details": {
                            "field": "email",
                            "issue": "Invalid email format"
                        }
                    },
                    "timestamp": "2025-01-01T12:00:00Z"
                }
            }
        }
    },
    401: {
        "description": "Unauthorized",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": {
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Invalid or expired token",
                        "details": {}
                    },
                    "timestamp": "2025-01-01T12:00:00Z"
                }
            }
        }
    },
    403: {
        "description": "Forbidden",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": {
                        "code": "AUTHORIZATION_ERROR",
                        "message": "Insufficient permissions",
                        "details": {}
                    },
                    "timestamp": "2025-01-01T12:00:00Z"
                }
            }
        }
    },
    404: {
        "description": "Not Found",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND_ERROR",
                        "message": "Resource not found",
                        "details": {
                            "resource_type": "hackathon",
                            "resource_id": "uuid-string"
                        }
                    },
                    "timestamp": "2025-01-01T12:00:00Z"
                }
            }
        }
    },
    409: {
        "description": "Conflict",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": {
                        "code": "DUPLICATE_ERROR",
                        "message": "Resource already exists",
                        "details": {
                            "field": "email",
                            "value": "user@example.com"
                        }
                    },
                    "timestamp": "2025-01-01T12:00:00Z"
                }
            }
        }
    },
    429: {
        "description": "Too Many Requests",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": {
                        "code": "RATE_LIMIT_ERROR",
                        "message": "Rate limit exceeded",
                        "details": {
                            "retry_after": 3600,
                            "limit": "1000 per hour"
                        }
                    },
                    "timestamp": "2025-01-01T12:00:00Z"
                }
            }
        }
    },
    500: {
        "description": "Internal Server Error",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "An unexpected error occurred",
                        "details": {}
                    },
                    "timestamp": "2025-01-01T12:00:00Z"
                }
            }
        }
    },
    502: {
        "description": "Bad Gateway",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": {
                        "code": "EXTERNAL_API_ERROR",
                        "message": "External service is unavailable",
                        "details": {
                            "service": "AI API",
                            "provider": "OpenAI"
                        }
                    },
                    "timestamp": "2025-01-01T12:00:00Z"
                }
            }
        }
    },
    503: {
        "description": "Service Unavailable",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "error": {
                        "code": "AI_SERVICE_ERROR",
                        "message": "AI service is temporarily unavailable",
                        "details": {
                            "retry_after": 60
                        }
                    },
                    "timestamp": "2025-01-01T12:00:00Z"
                }
            }
        }
    }
}


# Common error response schemas
COMMON_ERROR_RESPONSES = {
    400: ERROR_RESPONSES[400],
    401: ERROR_RESPONSES[401],
    403: ERROR_RESPONSES[403],
    500: ERROR_RESPONSES[500]
}