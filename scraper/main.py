"""
Main scraper orchestrator for HackSeek.
"""
import asyncio
import logging
from datetime import datetime
from typing import List

from config import Settings
from database import init_db, get_db_session
from scrapers.base_scraper import ScrapingResult
from scrapers.devpost_scraper import DevpostScraper
from scrapers.unstop_scraper import UnstopScraper
from scrapers.mlh_scraper import MLHScraper
from utils.logger import setup_logging

# Initialize settings and logging
settings = Settings()
setup_logging()
logger = logging.getLogger("scraper.main")


async def run_all_scrapers() -> List[ScrapingResult]:
    """Run all hackathon scrapers."""
    results = []

    scrapers = [
        DevpostScraper(),
        UnstopScraper(),
        MLHScraper()
    ]

    logger.info(f"Starting scraping run with {len(scrapers)} scrapers")

    for scraper in scrapers:
        try:
            logger.info(f"Running scraper: {scraper.name}")
            result = await scraper.scrape()
            results.append(result)

            logger.info(
                f"{scraper.name} completed: {result.hackathons_found} found, "
                f"{result.errors_count} errors"
            )

        except Exception as e:
            logger.error(f"Scraper {scraper.name} failed: {e}")
            results.append(ScrapingResult(
                platform=scraper.name,
                success=False,
                error_message=str(e)
            ))

    return results


async def main():
    """Main scraper entry point."""
    try:
        logger.info("HackSeek Scraper starting...")

        # Initialize database
        await init_db()

        # Run scrapers
        results = await run_all_scrapers()

        # Log summary
        total_found = sum(r.hackathons_found for r in results if r.success)
        total_errors = sum(r.errors_count for r in results)
        successful_scrapers = sum(1 for r in results if r.success)

        logger.info(
            f"Scraping completed: {successful_scrapers}/{len(results)} scrapers successful, "
            f"{total_found} hackathons found, {total_errors} errors"
        )

    except Exception as e:
        logger.error(f"Scraper failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())