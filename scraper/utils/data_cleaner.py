"""
Data cleaning and normalization utilities.
"""
import re
from datetime import datetime
from typing import Dict, Any, Optional, List


class DataCleaner:
    """Clean and normalize scraped hackathon data."""

    @staticmethod
    def clean_hackathon_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize hackathon data."""
        cleaned = {}

        # Clean title
        cleaned['title'] = DataCleaner._clean_text(data.get('title', ''))

        # Clean description
        cleaned['description'] = DataCleaner._clean_description(data.get('description'))

        # Clean URLs
        cleaned['website_url'] = DataCleaner._clean_url(data.get('website_url'))
        cleaned['registration_url'] = DataCleaner._clean_url(data.get('registration_url'))

        # Clean dates
        cleaned['start_date'] = DataCleaner._clean_date(data.get('start_date'))
        cleaned['end_date'] = DataCleaner._clean_date(data.get('end_date'))
        cleaned['registration_deadline'] = DataCleaner._clean_date(data.get('registration_deadline'))

        # Clean location
        cleaned['location'] = DataCleaner._clean_location(data.get('location'))
        cleaned['is_online'] = DataCleaner._normalize_boolean(data.get('is_online'))

        # Clean prize money
        cleaned['prize_money'] = DataCleaner._clean_prize_money(data.get('prize_money'))

        # Clean arrays
        cleaned['categories'] = DataCleaner._clean_array(data.get('categories'))
        cleaned['technologies'] = DataCleaner._clean_array(data.get('technologies'))

        # Clean organizer
        cleaned['organizer'] = DataCleaner._clean_text(data.get('organizer'))

        # Clean source data
        cleaned['source_platform'] = DataCleaner._clean_text(data.get('source_platform', ''))
        cleaned['source_id'] = DataCleaner._clean_text(data.get('source_id', ''))
        cleaned['source_url'] = DataCleaner._clean_url(data.get('source_url'))

        # Set defaults
        cleaned['is_active'] = True
        cleaned['scraped_at'] = datetime.utcnow()

        return cleaned

    @staticmethod
    def _clean_text(text: Any) -> Optional[str]:
        """Clean text fields."""
        if not text:
            return None

        if not isinstance(text, str):
            text = str(text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Remove HTML entities
        html_entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&apos;': "'",
            '&nbsp;': ' '
        }

        for entity, replacement in html_entities.items():
            text = text.replace(entity, replacement)

        return text if text else None

    @staticmethod
    def _clean_description(description: Any) -> Optional[str]:
        """Clean description with length limits."""
        cleaned = DataCleaner._clean_text(description)

        if not cleaned:
            return None

        # Limit description length
        if len(cleaned) > 5000:
            cleaned = cleaned[:4997] + "..."

        return cleaned

    @staticmethod
    def _clean_url(url: Any) -> Optional[str]:
        """Clean and validate URLs."""
        if not url:
            return None

        if not isinstance(url, str):
            url = str(url)

        url = url.strip()

        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                return None  # Relative URLs need base URL
            else:
                url = 'https://' + url

        # Basic URL format check
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if url_pattern.match(url):
            return url

        return None

    @staticmethod
    def _clean_date(date_value: Any) -> Optional[datetime]:
        """Clean and normalize dates."""
        if not date_value:
            return None

        if isinstance(date_value, datetime):
            return date_value

        if isinstance(date_value, str):
            # Try to parse common date formats
            date_formats = [
                '%Y-%m-%d',
                '%Y-%m-%d %H:%M:%S',
                '%m/%d/%Y',
                '%d/%m/%Y',
                '%b %d %Y',
                '%B %d, %Y'
            ]

            for fmt in date_formats:
                try:
                    return datetime.strptime(date_value.strip(), fmt)
                except ValueError:
                    continue

        return None

    @staticmethod
    def _clean_location(location: Any) -> Optional[str]:
        """Clean location field."""
        cleaned = DataCleaner._clean_text(location)

        if not cleaned:
            return None

        # Normalize common location formats
        location_mappings = {
            'online': 'Online',
            'virtual': 'Online',
            'remote': 'Online',
            'worldwide': 'Online',
            'global': 'Online'
        }

        cleaned_lower = cleaned.lower()
        for key, value in location_mappings.items():
            if key in cleaned_lower:
                return value

        return cleaned

    @staticmethod
    def _normalize_boolean(value: Any) -> bool:
        """Normalize boolean values."""
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on', 'online', 'virtual')

        if isinstance(value, (int, float)):
            return bool(value)

        return False

    @staticmethod
    def _clean_prize_money(prize: Any) -> Optional[float]:
        """Clean and normalize prize money."""
        if not prize:
            return None

        if isinstance(prize, (int, float)):
            return float(prize) if prize > 0 else None

        if isinstance(prize, str):
            # Remove currency symbols and commas
            cleaned = re.sub(r'[^\d.]', '', prize)
            try:
                value = float(cleaned)
                return value if value > 0 else None
            except ValueError:
                return None

        return None

    @staticmethod
    def _clean_array(arr: Any) -> List[str]:
        """Clean array fields like categories and technologies."""
        if not arr:
            return []

        if isinstance(arr, str):
            # Split string by common delimiters
            arr = re.split(r'[,;|]', arr)

        if not isinstance(arr, list):
            return []

        cleaned = []
        for item in arr:
            cleaned_item = DataCleaner._clean_text(item)
            if cleaned_item and len(cleaned_item) < 100:  # Reasonable length
                cleaned.append(cleaned_item)

        # Remove duplicates while preserving order
        seen = set()
        result = []
        for item in cleaned:
            if item.lower() not in seen:
                seen.add(item.lower())
                result.append(item)

        return result

    @staticmethod
    def detect_duplicates(hackathons: List[Dict[str, Any]]) -> List[tuple[int, int]]:
        """Detect potential duplicate hackathons."""
        duplicates = []

        for i, hack1 in enumerate(hackathons):
            for j, hack2 in enumerate(hackathons[i+1:], i+1):
                if DataCleaner._is_duplicate(hack1, hack2):
                    duplicates.append((i, j))

        return duplicates

    @staticmethod
    def _is_duplicate(hack1: Dict[str, Any], hack2: Dict[str, Any]) -> bool:
        """Check if two hackathons are duplicates."""
        # Same source and ID
        if (hack1.get('source_platform') == hack2.get('source_platform') and
            hack1.get('source_id') == hack2.get('source_id') and
            hack1.get('source_id')):
            return True

        # Same title (with fuzzy matching)
        title1 = hack1.get('title', '').lower().strip()
        title2 = hack2.get('title', '').lower().strip()

        if title1 and title2:
            # Simple similarity check
            if title1 == title2:
                return True

            # Check if one title contains the other
            if len(title1) > 10 and len(title2) > 10:
                if title1 in title2 or title2 in title1:
                    return True

        return False