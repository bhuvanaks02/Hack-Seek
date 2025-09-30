"""
HackerEarth hackathon scraper.
"""
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse

from .base_scraper import BaseScraper


class HackerEarthScraper(BaseScraper):
    """Scraper for HackerEarth hackathons."""

    @property
    def name(self) -> str:
        return "hackerearth"

    @property
    def base_url(self) -> str:
        return "https://www.hackerearth.com"

    async def get_hackathon_urls(self) -> List[str]:
        """Get hackathon URLs from HackerEarth."""
        urls = []

        # HackerEarth challenges page
        list_url = f"{self.base_url}/challenges/hackathon/"
        html = await self.fetch_page(list_url)

        if not html:
            return urls

        soup = self.parse_html(html)

        # Find challenge links
        challenge_links = soup.find_all('a', href=re.compile(r'/challenges/hackathon/'))

        for link in challenge_links:
            href = link.get('href')
            if href and href not in urls:
                full_url = urljoin(self.base_url, href)
                urls.append(full_url)

        self.logger.info(f"Found {len(urls)} hackathons on HackerEarth")
        return urls[:20]  # Limit for demo

    async def parse_hackathon(self, url: str) -> Optional[Dict[str, Any]]:
        """Parse a single HackerEarth hackathon page."""
        html = await self.fetch_page(url)
        if not html:
            return None

        soup = self.parse_html(html)

        try:
            # Title
            title_elem = soup.find('h1') or soup.find('h2')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"

            # Description
            desc_elem = soup.find('div', class_=re.compile(r'description|about'))
            description = desc_elem.get_text(strip=True) if desc_elem else None

            # Extract basic data
            hackathon_data = {
                "title": title,
                "description": description,
                "website_url": url,
                "registration_url": url,
                "location": "Online",
                "is_online": True,
                "categories": ["Hackathon", "Programming"],
                "source_id": self._extract_id(url),
                "source_url": url,
            }

            return hackathon_data

        except Exception as e:
            self.logger.error(f"Error parsing hackathon {url}: {e}")
            return None

    def _extract_id(self, url: str) -> str:
        """Extract HackerEarth hackathon ID."""
        try:
            return url.split('/')[-2] if url.endswith('/') else url.split('/')[-1]
        except:
            return url