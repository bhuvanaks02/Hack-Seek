"""
Devpost hackathon scraper.
"""
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse

from .base_scraper import BaseScraper


class DevpostScraper(BaseScraper):
    """Scraper for Devpost hackathons."""

    @property
    def name(self) -> str:
        return "devpost"

    @property
    def base_url(self) -> str:
        return "https://devpost.com"

    async def get_hackathon_urls(self) -> List[str]:
        """Get hackathon URLs from Devpost."""
        urls = []

        # Scrape hackathons list page
        list_url = f"{self.base_url}/hackathons?search="
        html = await self.fetch_page(list_url)

        if not html:
            return urls

        soup = self.parse_html(html)

        # Find hackathon links
        hackathon_links = soup.find_all('a', class_='link-to-software')

        for link in hackathon_links:
            href = link.get('href')
            if href:
                full_url = urljoin(self.base_url, href)
                urls.append(full_url)

        # Also check upcoming hackathons
        upcoming_url = f"{self.base_url}/hackathons?search=&challenge_type=all&sort_by=recently-added"
        html = await self.fetch_page(upcoming_url)

        if html:
            soup = self.parse_html(html)
            upcoming_links = soup.find_all('a', class_='link-to-software')

            for link in upcoming_links:
                href = link.get('href')
                if href:
                    full_url = urljoin(self.base_url, href)
                    if full_url not in urls:
                        urls.append(full_url)

        self.logger.info(f"Found {len(urls)} hackathons on Devpost")
        return urls

    async def parse_hackathon(self, url: str) -> Optional[Dict[str, Any]]:
        """Parse a single Devpost hackathon page."""
        html = await self.fetch_page(url)
        if not html:
            return None

        soup = self.parse_html(html)

        try:
            # Extract basic info
            title_elem = soup.find('h1', id='challenge-title')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"

            # Description
            description_elem = soup.find('div', class_='challenge-description')
            description = description_elem.get_text(strip=True) if description_elem else None

            # Dates
            dates_section = soup.find('div', class_='challenge-dates')
            start_date, end_date = self._parse_dates(dates_section)

            # Prize money
            prize_money = self._extract_prize_money(soup)

            # Location and online status
            location_elem = soup.find('span', class_='challenge-location')
            location = location_elem.get_text(strip=True) if location_elem else None
            is_online = self._is_online_event(soup, location)

            # Categories/themes
            categories = self._extract_categories(soup)

            # Technologies
            technologies = self._extract_technologies(soup)

            # Registration URL (same as main URL for Devpost)
            registration_url = url

            # Extract source ID from URL
            source_id = self._extract_devpost_id(url)

            hackathon_data = {
                "title": title,
                "description": description,
                "website_url": url,
                "registration_url": registration_url,
                "start_date": start_date,
                "end_date": end_date,
                "location": location,
                "is_online": is_online,
                "prize_money": prize_money,
                "categories": categories,
                "technologies": technologies,
                "source_id": source_id,
                "source_url": url,
            }

            self.logger.debug(f"Parsed hackathon: {title}")
            return hackathon_data

        except Exception as e:
            self.logger.error(f"Error parsing hackathon {url}: {e}")
            return None

    def _parse_dates(self, dates_section) -> tuple[Optional[datetime], Optional[datetime]]:
        """Parse start and end dates from dates section."""
        if not dates_section:
            return None, None

        try:
            # Look for date patterns
            date_text = dates_section.get_text()

            # Common patterns: "Mar 15 - Mar 17, 2024"
            date_pattern = r'(\w{3}\s+\d{1,2})\s*-\s*(\w{3}\s+\d{1,2}),?\s*(\d{4})'
            match = re.search(date_pattern, date_text)

            if match:
                start_str = f"{match.group(1)} {match.group(3)}"
                end_str = f"{match.group(2)} {match.group(3)}"

                start_date = datetime.strptime(start_str, "%b %d %Y")
                end_date = datetime.strptime(end_str, "%b %d %Y")

                return start_date, end_date

        except Exception as e:
            self.logger.debug(f"Error parsing dates: {e}")

        return None, None

    def _extract_prize_money(self, soup) -> Optional[float]:
        """Extract prize money from the page."""
        try:
            # Look for prize sections
            prize_sections = soup.find_all(['div', 'span'], string=re.compile(r'\$[\d,]+'))

            for section in prize_sections:
                text = section.get_text()
                # Find dollar amounts
                amounts = re.findall(r'\$([0-9,]+)', text)

                if amounts:
                    # Take the largest amount
                    max_amount = max(int(amount.replace(',', '')) for amount in amounts)
                    return float(max_amount)

        except Exception as e:
            self.logger.debug(f"Error extracting prize money: {e}")

        return None

    def _is_online_event(self, soup, location: Optional[str]) -> bool:
        """Determine if event is online."""
        if not location:
            return True

        online_keywords = ['online', 'virtual', 'remote', 'worldwide', 'global']
        location_lower = location.lower()

        return any(keyword in location_lower for keyword in online_keywords)

    def _extract_categories(self, soup) -> List[str]:
        """Extract hackathon categories/themes."""
        categories = []

        try:
            # Look for theme or category sections
            theme_sections = soup.find_all(['div', 'span'], class_=re.compile(r'theme|category'))

            for section in theme_sections:
                text = section.get_text(strip=True)
                if text and len(text) < 50:  # Reasonable category name length
                    categories.append(text)

            # Common Devpost categories
            common_categories = ['AI/ML', 'Web Development', 'Mobile', 'Gaming', 'IoT', 'Blockchain']
            page_text = soup.get_text().lower()

            for category in common_categories:
                if category.lower() in page_text:
                    categories.append(category)

        except Exception as e:
            self.logger.debug(f"Error extracting categories: {e}")

        return list(set(categories))  # Remove duplicates

    def _extract_technologies(self, soup) -> List[str]:
        """Extract suggested technologies."""
        technologies = []

        try:
            # Look for technology mentions
            tech_keywords = [
                'Python', 'JavaScript', 'React', 'Node.js', 'Django', 'Flask',
                'Java', 'C++', 'Swift', 'Kotlin', 'Unity', 'TensorFlow',
                'AWS', 'Azure', 'GCP', 'Docker', 'MongoDB', 'PostgreSQL'
            ]

            page_text = soup.get_text()

            for tech in tech_keywords:
                if tech in page_text:
                    technologies.append(tech)

        except Exception as e:
            self.logger.debug(f"Error extracting technologies: {e}")

        return technologies

    def _extract_devpost_id(self, url: str) -> str:
        """Extract Devpost hackathon ID from URL."""
        try:
            # URLs like: https://devpost.com/software/hackathon-name
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')

            if len(path_parts) >= 2 and path_parts[0] == 'software':
                return path_parts[1]

            # Fallback: use the last part of the path
            return path_parts[-1] if path_parts else url

        except Exception:
            return url