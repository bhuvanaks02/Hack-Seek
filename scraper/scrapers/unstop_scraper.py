"""
Unstop (formerly Dare2Compete) hackathon scraper.
"""
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse

from .base_scraper import BaseScraper


class UnstopScraper(BaseScraper):
    """Scraper for Unstop hackathons."""

    @property
    def name(self) -> str:
        return "unstop"

    @property
    def base_url(self) -> str:
        return "https://unstop.com"

    async def get_hackathon_urls(self) -> List[str]:
        """Get hackathon URLs from Unstop."""
        urls = []

        # Unstop hackathons page
        list_url = f"{self.base_url}/hackathons"
        html = await self.fetch_page(list_url)

        if not html:
            return urls

        soup = self.parse_html(html)

        # Find hackathon cards
        hackathon_cards = soup.find_all('div', class_=re.compile(r'opportunity-card|competition-card'))

        for card in hackathon_cards:
            link = card.find('a')
            if link:
                href = link.get('href')
                if href:
                    full_url = urljoin(self.base_url, href)
                    urls.append(full_url)

        # Also check specific hackathon listings
        categories = ['hackathons', 'coding-competitions']

        for category in categories:
            category_url = f"{self.base_url}/{category}"
            html = await self.fetch_page(category_url)

            if html:
                soup = self.parse_html(html)
                links = soup.find_all('a', href=re.compile(r'/o/'))

                for link in links:
                    href = link.get('href')
                    if href:
                        full_url = urljoin(self.base_url, href)
                        if full_url not in urls:
                            urls.append(full_url)

        self.logger.info(f"Found {len(urls)} hackathons on Unstop")
        return urls

    async def parse_hackathon(self, url: str) -> Optional[Dict[str, Any]]:
        """Parse a single Unstop hackathon page."""
        html = await self.fetch_page(url)
        if not html:
            return None

        soup = self.parse_html(html)

        try:
            # Title
            title_elem = soup.find('h1') or soup.find('h2', class_=re.compile(r'title|heading'))
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"

            # Description
            description = self._extract_description(soup)

            # Dates
            start_date, end_date, registration_deadline = self._parse_dates(soup)

            # Prize money
            prize_money = self._extract_prize_money(soup)

            # Location
            location, is_online = self._extract_location(soup)

            # Categories
            categories = self._extract_categories(soup)

            # Extract source ID from URL
            source_id = self._extract_unstop_id(url)

            # Registration URL
            registration_url = self._find_registration_url(soup, url)

            hackathon_data = {
                "title": title,
                "description": description,
                "website_url": url,
                "registration_url": registration_url,
                "start_date": start_date,
                "end_date": end_date,
                "registration_deadline": registration_deadline,
                "location": location,
                "is_online": is_online,
                "prize_money": prize_money,
                "categories": categories,
                "technologies": self._extract_technologies(soup),
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
            'div[class*="description"]',
            'div[class*="about"]',
            'div[class*="details"]',
            'p[class*="description"]'
        ]

        for selector in desc_selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                if len(text) > 50:  # Reasonable description length
                    return text

        return None

    def _parse_dates(self, soup) -> tuple[Optional[datetime], Optional[datetime], Optional[datetime]]:
        """Parse dates from the page."""
        try:
            # Look for date sections
            date_elements = soup.find_all(['div', 'span'], string=re.compile(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}|\w{3}\s+\d{1,2}'))

            dates = []
            for elem in date_elements:
                text = elem.get_text()
                # Extract date patterns
                date_patterns = [
                    r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY
                    r'(\w{3})\s+(\d{1,2}),?\s*(\d{4})',     # Mar 15, 2024
                ]

                for pattern in date_patterns:
                    matches = re.findall(pattern, text)
                    for match in matches:
                        try:
                            if pattern.startswith(r'(\d'):  # DD/MM/YYYY format
                                date_obj = datetime.strptime(f"{match[0]}/{match[1]}/{match[2]}", "%d/%m/%Y")
                            else:  # Month name format
                                date_obj = datetime.strptime(f"{match[0]} {match[1]} {match[2]}", "%b %d %Y")
                            dates.append(date_obj)
                        except ValueError:
                            continue

            if dates:
                dates.sort()
                start_date = dates[0] if len(dates) > 0 else None
                end_date = dates[-1] if len(dates) > 1 else None
                registration_deadline = dates[0] if len(dates) == 1 else None

                return start_date, end_date, registration_deadline

        except Exception as e:
            self.logger.debug(f"Error parsing dates: {e}")

        return None, None, None

    def _extract_prize_money(self, soup) -> Optional[float]:
        """Extract prize money."""
        try:
            # Look for prize mentions
            prize_text = soup.get_text()

            # Indian currency patterns
            inr_patterns = [
                r'₹\s*([0-9,]+)(?:\s*(?:lakhs?|crores?))?',
                r'INR\s*([0-9,]+)',
                r'Rs\.?\s*([0-9,]+)'
            ]

            # USD patterns
            usd_patterns = [
                r'\$\s*([0-9,]+)',
                r'USD\s*([0-9,]+)'
            ]

            max_amount = 0

            # Check INR amounts
            for pattern in inr_patterns:
                matches = re.findall(pattern, prize_text, re.IGNORECASE)
                for match in matches:
                    amount = int(match.replace(',', ''))
                    # Convert lakhs/crores
                    if 'lakh' in prize_text.lower():
                        amount *= 100000
                    elif 'crore' in prize_text.lower():
                        amount *= 10000000

                    # Convert INR to USD (approximate)
                    amount_usd = amount / 83  # Rough conversion rate
                    max_amount = max(max_amount, amount_usd)

            # Check USD amounts
            for pattern in usd_patterns:
                matches = re.findall(pattern, prize_text, re.IGNORECASE)
                for match in matches:
                    amount = int(match.replace(',', ''))
                    max_amount = max(max_amount, amount)

            return float(max_amount) if max_amount > 0 else None

        except Exception as e:
            self.logger.debug(f"Error extracting prize money: {e}")

        return None

    def _extract_location(self, soup) -> tuple[Optional[str], bool]:
        """Extract location and determine if online."""
        try:
            location_elements = soup.find_all(['div', 'span'], string=re.compile(r'location|venue', re.IGNORECASE))

            for elem in location_elements:
                location_text = elem.get_text(strip=True)

                online_keywords = ['online', 'virtual', 'remote', 'pan india', 'worldwide']
                is_online = any(keyword in location_text.lower() for keyword in online_keywords)

                if location_text and len(location_text) < 100:
                    return location_text, is_online

            # Default to online if no location found
            return "Online", True

        except Exception as e:
            self.logger.debug(f"Error extracting location: {e}")

        return "Online", True

    def _extract_categories(self, soup) -> List[str]:
        """Extract categories/themes."""
        categories = []

        try:
            # Look for category tags or labels
            category_elements = soup.find_all(['span', 'div'], class_=re.compile(r'tag|category|theme'))

            for elem in category_elements:
                text = elem.get_text(strip=True)
                if text and len(text) < 50:
                    categories.append(text)

            # Common Unstop categories
            page_text = soup.get_text().lower()
            common_categories = [
                'hackathon', 'coding', 'programming', 'ai/ml', 'web development',
                'mobile app', 'blockchain', 'iot', 'data science', 'cybersecurity'
            ]

            for category in common_categories:
                if category in page_text:
                    categories.append(category.title())

        except Exception as e:
            self.logger.debug(f"Error extracting categories: {e}")

        return list(set(categories))

    def _extract_technologies(self, soup) -> List[str]:
        """Extract technologies."""
        technologies = []

        try:
            tech_keywords = [
                'Python', 'Java', 'JavaScript', 'C++', 'React', 'Angular',
                'Node.js', 'Django', 'Flask', 'MongoDB', 'MySQL', 'AWS'
            ]

            page_text = soup.get_text()

            for tech in tech_keywords:
                if tech in page_text:
                    technologies.append(tech)

        except Exception as e:
            self.logger.debug(f"Error extracting technologies: {e}")

        return technologies

    def _extract_unstop_id(self, url: str) -> str:
        """Extract Unstop hackathon ID from URL."""
        try:
            # URLs like: https://unstop.com/o/hackathon-name/123456
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')

            # Look for numeric ID
            for part in path_parts:
                if part.isdigit():
                    return part

            # Fallback to last path segment
            return path_parts[-1] if path_parts else url

        except Exception:
            return url

    def _find_registration_url(self, soup, current_url: str) -> str:
        """Find registration URL."""
        # Look for registration buttons
        register_buttons = soup.find_all(['a', 'button'], string=re.compile(r'register|apply|participate', re.IGNORECASE))

        for button in register_buttons:
            href = button.get('href')
            if href:
                return urljoin(self.base_url, href)

        # Default to current URL
        return current_url