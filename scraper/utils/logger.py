"""
Logging configuration for scraper service.
"""
import logging
import sys
from pathlib import Path


def setup_logging(level: str = "INFO"):
    """Set up logging configuration."""

    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "scraper.log")
        ]
    )