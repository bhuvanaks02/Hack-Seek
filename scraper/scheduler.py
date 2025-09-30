"""
Scraping scheduler for automated hackathon data collection.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict

from config import settings
from main import run_all_scrapers
from utils.logger import setup_logging


class ScrapingScheduler:
    """Schedule and manage scraping jobs."""

    def __init__(self):
        setup_logging()
        self.logger = logging.getLogger("scraper.scheduler")
        self.running = False

    async def start_scheduler(self):
        """Start the scraping scheduler."""
        self.logger.info("Starting scraping scheduler...")
        self.running = True

        while self.running:
            try:
                # Run scrapers
                self.logger.info("Starting scheduled scraping run")
                results = await run_all_scrapers()

                # Log results
                successful = sum(1 for r in results if r.success)
                total_hackathons = sum(r.hackathons_found for r in results if r.success)

                self.logger.info(
                    f"Scheduled run completed: {successful}/{len(results)} scrapers successful, "
                    f"{total_hackathons} hackathons found"
                )

                # Wait for next run (configurable interval)
                interval_hours = getattr(settings, 'scraping_interval_hours', 6)
                self.logger.info(f"Next run in {interval_hours} hours")

                await asyncio.sleep(interval_hours * 3600)

            except Exception as e:
                self.logger.error(f"Scheduled scraping failed: {e}")
                # Wait 1 hour before retrying on error
                await asyncio.sleep(3600)

    def stop_scheduler(self):
        """Stop the scheduler."""
        self.logger.info("Stopping scraping scheduler...")
        self.running = False


async def main():
    """Main scheduler entry point."""
    scheduler = ScrapingScheduler()

    try:
        await scheduler.start_scheduler()
    except KeyboardInterrupt:
        scheduler.stop_scheduler()
        print("Scheduler stopped by user")


if __name__ == "__main__":
    asyncio.run(main())