"""
Base scraper class for all hackathon scrapers.
"""
import asyncio
import aiohttp
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

from ..config import settings
from ..database import save_hackathon, save_scraping_job


@dataclass
class ScrapingResult:
    """Result of a scraping operation."""
    platform: str
    success: bool
    hackathons_found: int = 0
    hackathons_saved: int = 0
    errors_count: int = 0
    error_message: Optional[str] = None
    duration_seconds: float = 0.0


class BaseScraper(ABC):
    """Base class for all scrapers."""

    def __init__(self):
        self.logger = logging.getLogger(f"scraper.{self.name}")
        self.session: Optional[aiohttp.ClientSession] = None
        self.hackathons_found = 0
        self.hackathons_saved = 0
        self.errors_count = 0

    @property
    @abstractmethod
    def name(self) -> str:
        """Scraper name."""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Base URL for the platform."""
        pass

    async def create_session(self) -> aiohttp.ClientSession:
        """Create HTTP session with common settings."""
        headers = {
            "User-Agent": settings.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

        timeout = aiohttp.ClientTimeout(total=settings.request_timeout)

        return aiohttp.ClientSession(
            headers=headers,
            timeout=timeout,
            connector=aiohttp.TCPConnector(limit=10)
        )

    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch a web page with error handling."""
        try:
            await asyncio.sleep(settings.scraping_delay)  # Rate limiting

            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    self.logger.warning(f"HTTP {response.status} for {url}")
                    self.errors_count += 1
                    return None

        except Exception as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            self.errors_count += 1
            return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content."""
        return BeautifulSoup(html, 'html.parser')

    @abstractmethod
    async def get_hackathon_urls(self) -> List[str]:
        """Get list of hackathon URLs to scrape."""
        pass

    @abstractmethod
    async def parse_hackathon(self, url: str) -> Optional[Dict[str, Any]]:
        """Parse a single hackathon page."""
        pass

    async def save_hackathon_data(self, hackathon_data: Dict[str, Any]) -> bool:
        """Save hackathon data to database."""
        hackathon_data.update({
            "source_platform": self.name,
            "scraped_at": datetime.utcnow()
        })

        success = await save_hackathon(hackathon_data)
        if success:
            self.hackathons_saved += 1

        return success

    async def scrape(self) -> ScrapingResult:
        """Main scraping method."""
        start_time = datetime.utcnow()

        try:
            self.session = await self.create_session()
            self.logger.info(f"Starting {self.name} scraper")

            # Get hackathon URLs
            urls = await self.get_hackathon_urls()
            self.logger.info(f"Found {len(urls)} hackathons to scrape")

            # Process each hackathon
            for url in urls[:50]:  # Limit to 50 for now
                try:
                    hackathon_data = await self.parse_hackathon(url)
                    if hackathon_data:
                        await self.save_hackathon_data(hackathon_data)
                        self.hackathons_found += 1

                except Exception as e:
                    self.logger.error(f"Error parsing {url}: {e}")
                    self.errors_count += 1

            # Calculate duration
            duration = (datetime.utcnow() - start_time).total_seconds()

            # Save scraping job
            await save_scraping_job(
                platform=self.name,
                status="completed",
                hackathons_scraped=self.hackathons_saved,
                errors_encountered=self.errors_count
            )

            return ScrapingResult(
                platform=self.name,
                success=True,
                hackathons_found=self.hackathons_found,
                hackathons_saved=self.hackathons_saved,
                errors_count=self.errors_count,
                duration_seconds=duration
            )

        except Exception as e:
            self.logger.error(f"Scraper failed: {e}")

            # Save failed job
            await save_scraping_job(
                platform=self.name,
                status="failed",
                hackathons_scraped=self.hackathons_saved,
                errors_encountered=self.errors_count,
                error_details={"error": str(e)}
            )

            return ScrapingResult(
                platform=self.name,
                success=False,
                error_message=str(e)
            )

        finally:
            if self.session:
                await self.session.close()