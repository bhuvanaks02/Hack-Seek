"""
Centralized logging configuration for the HackSeek backend application.
"""
import logging
import logging.handlers
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config import settings


class ColoredFormatter(logging.Formatter):
    """Colored log formatter for console output."""

    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record):
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}"
                f"{self.COLORS['RESET']}"
            )
        return super().format(record)


class StructuredFormatter(logging.Formatter):
    """Structured JSON-like formatter for log files."""

    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'ip_address'):
            log_entry['ip_address'] = record.ip_address

        return str(log_entry)


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    enable_console: bool = True
) -> logging.Logger:
    """
    Set up application logging configuration.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        enable_console: Whether to enable console logging

    Returns:
        Configured logger instance
    """
    # Determine log level
    if level is None:
        level = 'DEBUG' if settings.debug else 'INFO'

    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))

        if sys.stdout.isatty():  # Terminal supports colors
            console_formatter = ColoredFormatter(
                '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            console_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # File handler for general logs
    if log_file is None:
        log_file = log_dir / 'hackseek.log'
    else:
        log_file = Path(log_file)

    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, level.upper()))
    file_formatter = StructuredFormatter()
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Separate error log file
    error_file = log_dir / 'errors.log'
    error_handler = logging.handlers.RotatingFileHandler(
        error_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)

    # Access log file for HTTP requests
    access_file = log_dir / 'access.log'
    access_handler = logging.handlers.RotatingFileHandler(
        access_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    access_handler.setLevel(logging.INFO)
    access_formatter = logging.Formatter(
        '%(asctime)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    access_handler.setFormatter(access_formatter)

    # Create access logger
    access_logger = logging.getLogger('access')
    access_logger.addHandler(access_handler)
    access_logger.setLevel(logging.INFO)
    access_logger.propagate = False  # Don't propagate to root logger

    # Configure third-party loggers
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(
        logging.INFO if settings.debug else logging.WARNING
    )

    # Application logger
    app_logger = logging.getLogger('hackseek')
    app_logger.info(f"Logging initialized - Level: {level}, File: {log_file}")

    return app_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name."""
    return logging.getLogger(f"hackseek.{name}")


def log_request(
    method: str,
    url: str,
    status_code: int,
    response_time: float,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None
) -> None:
    """Log HTTP request information."""
    access_logger = logging.getLogger('access')
    message = f"{method} {url} {status_code} {response_time:.3f}s"

    if user_id:
        message += f" user:{user_id}"
    if ip_address:
        message += f" ip:{ip_address}"

    access_logger.info(message)


def log_exception(
    logger: logging.Logger,
    message: str,
    exc_info: bool = True,
    **extra
) -> None:
    """Log exception with additional context."""
    logger.error(message, exc_info=exc_info, extra=extra)


# Context manager for adding request context to logs
class LogContext:
    """Context manager to add request-specific data to log records."""

    def __init__(self, **context):
        self.context = context
        self.old_factory = logging.getLogRecordFactory()

    def __enter__(self):
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record

        logging.setLogRecordFactory(record_factory)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.setLogRecordFactory(self.old_factory)