"""
Major League Hacking (MLH) hackathon scraper.
"""
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse

from .base_scraper import BaseScraper


class MLHScraper(BaseScraper):
    """Scraper for MLH hackathons."""

    @property
    def name(self) -> str:
        return "mlh"

    @property
    def base_url(self) -> str:
        return "https://mlh.io"

    async def get_hackathon_urls(self) -> List[str]:
        """Get hackathon URLs from MLH."""
        urls = []

        # MLH events page
        events_url = f"{self.base_url}/seasons/2024/events"
        html = await self.fetch_page(events_url)

        if not html:
            return urls

        soup = self.parse_html(html)

        # Find event links
        event_links = soup.find_all('a', href=re.compile(r'/events/'))

        for link in event_links:
            href = link.get('href')
            if href:
                full_url = urljoin(self.base_url, href)
                urls.append(full_url)

        # Also check upcoming events
        upcoming_url = f"{self.base_url}/events"
        html = await self.fetch_page(upcoming_url)

        if html:
            soup = self.parse_html(html)
            upcoming_links = soup.find_all('a', href=re.compile(r'/events/'))

            for link in upcoming_links:
                href = link.get('href')
                if href:
                    full_url = urljoin(self.base_url, href)
                    if full_url not in urls:
                        urls.append(full_url)

        self.logger.info(f"Found {len(urls)} hackathons on MLH")
        return urls

    async def parse_hackathon(self, url: str) -> Optional[Dict[str, Any]]:
        """Parse a single MLH hackathon page."""
        html = await self.fetch_page(url)
        if not html:
            return None

        soup = self.parse_html(html)

        try:
            # Title
            title_elem = soup.find('h1') or soup.find('h2', class_='event-name')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"

            # Description
            description = self._extract_description(soup)

            # Dates
            start_date, end_date = self._parse_dates(soup)

            # Location
            location, is_online = self._extract_location(soup)

            # Registration URL
            registration_url = self._find_registration_url(soup)

            # Categories (MLH hackathons are generally coding/tech focused)
            categories = ['Hackathon', 'Programming', 'Technology']

            # Extract source ID from URL
            source_id = self._extract_mlh_id(url)

            # MLH hackathons typically don't list specific prize money
            # But they often have sponsor prizes
            prize_money = self._extract_prize_info(soup)

            hackathon_data = {
                "title": title,
                "description": description,
                "website_url": url,
                "registration_url": registration_url or url,
                "start_date": start_date,
                "end_date": end_date,
                "location": location,
                "is_online": is_online,
                "prize_money": prize_money,
                "categories": categories,
                "technologies": self._extract_technologies(soup),
                "organizer": "MLH",
                "source_id": source_id,
                "source_url": url,
            }

            self.logger.debug(f"Parsed hackathon: {title}")
            return hackathon_data

        except Exception as e:
            self.logger.error(f"Error parsing hackathon {url}: {e}")
            return None

    def _extract_description(self, soup) -> Optional[str]:
        """Extract hackathon description."""
        # Look for description sections
        desc_selectors = [
            'div.event-description',
            'div[class*="description"]',
            'div[class*="about"]',
            'section.about'
        ]

        for selector in desc_selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                if len(text) > 50:
                    return text

        # Fallback: look for paragraphs with substantial text
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 100:  # Substantial content
                return text

        return None

    def _parse_dates(self, soup) -> tuple[Optional[datetime], Optional[datetime]]:
        """Parse start and end dates."""
        try:
            # Look for date sections
            date_elements = soup.find_all(['div', 'span', 'time'], class_=re.compile(r'date|time'))

            dates = []
            for elem in date_elements:
                text = elem.get_text()

                # Common MLH date formats
                date_patterns = [
                    r'(\w{3})\s+(\d{1,2}),?\s*(\d{4})',     # Mar 15, 2024
                    r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',   # 15/03/2024
                    r'(\w{3})\s+(\d{1,2})\s*-\s*(\d{1,2}),?\s*(\d{4})'  # Mar 15-17, 2024
                ]

                for pattern in date_patterns:
                    matches = re.findall(pattern, text)
                    for match in matches:
                        try:
                            if pattern.startswith(r'(\w'):  # Month name format
                                date_str = f"{match[0]} {match[1]} {match[2]}"
                                date_obj = datetime.strptime(date_str, "%b %d %Y")
                                dates.append(date_obj)
                            elif '/' in pattern:  # DD/MM/YYYY format
                                date_obj = datetime.strptime(f"{match[0]}/{match[1]}/{match[2]}", "%d/%m/%Y")
                                dates.append(date_obj)
                        except ValueError:
                            continue

            # Also check for specific patterns like "March 15-17, 2024"
            full_text = soup.get_text()
            range_pattern = r'(\w{3})\s+(\d{1,2})\s*-\s*(\d{1,2}),?\s*(\d{4})'
            range_matches = re.findall(range_pattern, full_text)

            for match in range_matches:
                try:
                    month, start_day, end_day, year = match
                    start_date = datetime.strptime(f"{month} {start_day} {year}", "%b %d %Y")
                    end_date = datetime.strptime(f"{month} {end_day} {year}", "%b %d %Y")
                    return start_date, end_date
                except ValueError:
                    continue

            if dates:
                dates.sort()
                return dates[0], dates[-1] if len(dates) > 1 else dates[0]

        except Exception as e:
            self.logger.debug(f"Error parsing dates: {e}")

        return None, None

    def _extract_location(self, soup) -> tuple[Optional[str], bool]:
        """Extract location and determine if online."""
        try:
            # Look for location information
            location_selectors = [
                '.event-location',
                '.location',
                '[class*="location"]'
            ]

            for selector in location_selectors:
                elem = soup.select_one(selector)
                if elem:
                    location_text = elem.get_text(strip=True)

                    # Check if online
                    online_keywords = ['online', 'virtual', 'remote', 'digital']
                    is_online = any(keyword in location_text.lower() for keyword in online_keywords)

                    return location_text, is_online

            # Look in general text for location patterns
            text = soup.get_text()
            location_patterns = [
                r'Location:\s*([^\n]+)',
                r'Venue:\s*([^\n]+)',
                r'Where:\s*([^\n]+)'
            ]

            for pattern in location_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    location = match.group(1).strip()
                    online_keywords = ['online', 'virtual', 'remote']
                    is_online = any(keyword in location.lower() for keyword in online_keywords)
                    return location, is_online

        except Exception as e:
            self.logger.debug(f"Error extracting location: {e}")

        # Default to online
        return "Online", True

    def _find_registration_url(self, soup) -> Optional[str]:
        """Find registration URL."""
        try:
            # Look for registration links
            register_buttons = soup.find_all(['a', 'button'], string=re.compile(r'register|apply|sign up', re.IGNORECASE))

            for button in register_buttons:
                href = button.get('href')
                if href:
                    if href.startswith('http'):
                        return href
                    else:
                        return urljoin(self.base_url, href)

            # Look for external registration links
            external_links = soup.find_all('a', href=re.compile(r'https?://(?!mlh\.io)'))
            for link in external_links:
                link_text = link.get_text().lower()
                if any(word in link_text for word in ['register', 'apply', 'sign up']):
                    return link.get('href')

        except Exception as e:
            self.logger.debug(f"Error finding registration URL: {e}")

        return None

    def _extract_prize_info(self, soup) -> Optional[float]:
        """Extract prize information."""
        try:
            text = soup.get_text().lower()

            # Look for prize mentions
            prize_patterns = [
                r'\$([0-9,]+)',
                r'(\d+)\s*k\s*in\s*prizes',
                r'prizes?\s*worth\s*\$?([0-9,]+)'
            ]

            max_amount = 0

            for pattern in prize_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0] if match[0] else match[1]

                    # Convert "k" notation
                    if 'k' in pattern:
                        amount = int(match) * 1000
                    else:
                        amount = int(match.replace(',', ''))

                    max_amount = max(max_amount, amount)

            return float(max_amount) if max_amount > 0 else None

        except Exception as e:
            self.logger.debug(f"Error extracting prize info: {e}")

        return None

    def _extract_technologies(self, soup) -> List[str]:
        """Extract suggested technologies."""
        technologies = []

        try:
            # Common technologies mentioned at MLH hackathons
            tech_keywords = [
                'Python', 'JavaScript', 'Java', 'C++', 'React', 'Node.js',
                'Django', 'Flask', 'MongoDB', 'PostgreSQL', 'AWS', 'Docker',
                'Machine Learning', 'AI', 'Blockchain', 'Mobile Development'
            ]

            text = soup.get_text()

            for tech in tech_keywords:
                if tech.lower() in text.lower():
                    technologies.append(tech)

            # Look for sponsor technologies
            sponsor_sections = soup.find_all(['div', 'section'], class_=re.compile(r'sponsor'))
            for section in sponsor_sections:
                section_text = section.get_text()
                for tech in tech_keywords:
                    if tech.lower() in section_text.lower() and tech not in technologies:
                        technologies.append(tech)

        except Exception as e:
            self.logger.debug(f"Error extracting technologies: {e}")

        return technologies

    def _extract_mlh_id(self, url: str) -> str:
        """Extract MLH event ID from URL."""
        try:
            # URLs like: https://mlh.io/events/hackathon-name-2024
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')

            if len(path_parts) >= 2 and path_parts[0] == 'events':
                return path_parts[1]

            return path_parts[-1] if path_parts else url

        except Exception:
            return url