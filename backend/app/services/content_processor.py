"""
Content processing and summarization service
"""
import re
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import aiohttp
import asyncio
from app.models.hackathon import Hackathon
import logging

logger = logging.getLogger(__name__)

@dataclass
class ContentSummary:
    summary: str
    key_points: List[str]
    technologies: List[str]
    categories: List[str]
    difficulty_assessment: str

class ContentProcessor:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.use_openai = bool(self.openai_api_key)

    async def summarize_hackathon(self, hackathon: Hackathon) -> ContentSummary:
        """Generate AI-powered summary and analysis of hackathon content"""
        try:
            if self.use_openai:
                return await self._openai_summarize(hackathon)
            else:
                return self._local_summarize(hackathon)
        except Exception as e:
            logger.error(f"Error summarizing hackathon {hackathon.id}: {e}")
            return self._fallback_summary(hackathon)

    async def _openai_summarize(self, hackathon: Hackathon) -> ContentSummary:
        """Use OpenAI to summarize hackathon content"""
        try:
            async with aiohttp.ClientSession() as session:
                content = self._prepare_content_for_analysis(hackathon)

                prompt = f"""
                Analyze this hackathon and provide:
                1. A concise 2-sentence summary
                2. 3-5 key points about the event
                3. Technical requirements/technologies mentioned
                4. Relevant categories (AI/ML, Web Development, Mobile, etc.)
                5. Difficulty assessment (Beginner/Intermediate/Advanced)

                Hackathon Details:
                {content}

                Return JSON format:
                {{
                    "summary": "...",
                    "key_points": [...],
                    "technologies": [...],
                    "categories": [...],
                    "difficulty_assessment": "..."
                }}
                """

                response = await self._call_openai_chat(session, prompt)

                if response:
                    import json
                    try:
                        data = json.loads(response)
                        return ContentSummary(
                            summary=data.get("summary", ""),
                            key_points=data.get("key_points", []),
                            technologies=data.get("technologies", []),
                            categories=data.get("categories", []),
                            difficulty_assessment=data.get("difficulty_assessment", "Intermediate")
                        )
                    except json.JSONDecodeError:
                        logger.error("Failed to parse OpenAI summary response")

                return self._local_summarize(hackathon)

        except Exception as e:
            logger.error(f"Error in OpenAI summarization: {e}")
            return self._local_summarize(hackathon)

    def _local_summarize(self, hackathon: Hackathon) -> ContentSummary:
        """Local summarization using rule-based approach"""
        try:
            # Extract key information
            content = hackathon.description or hackathon.short_description or ""
            title = hackathon.title or ""

            # Generate summary
            summary = self._extract_summary(title, content)

            # Extract key points
            key_points = self._extract_key_points(content)

            # Detect technologies
            technologies = self._detect_technologies(title + " " + content)

            # Classify categories
            categories = self._classify_categories(title + " " + content)

            # Assess difficulty
            difficulty = self._assess_difficulty(content, hackathon.difficulty_level)

            return ContentSummary(
                summary=summary,
                key_points=key_points,
                technologies=technologies,
                categories=categories,
                difficulty_assessment=difficulty
            )

        except Exception as e:
            logger.error(f"Error in local summarization: {e}")
            return self._fallback_summary(hackathon)

    def _extract_summary(self, title: str, content: str) -> str:
        """Extract or generate a summary"""
        if not content:
            return f"{title} - Details to be announced."

        # Take first 2 sentences or 200 characters
        sentences = re.split(r'[.!?]+', content)
        if len(sentences) >= 2:
            return f"{sentences[0].strip()}. {sentences[1].strip()}."
        elif len(content) > 200:
            return content[:200].rsplit(' ', 1)[0] + "..."
        else:
            return content.strip()

    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from content"""
        if not content:
            return []

        key_points = []

        # Look for prize information
        prize_patterns = [
            r'\$[\d,]+',
            r'prize.*\$[\d,]+',
            r'win.*\$[\d,]+',
            r'award.*\$[\d,]+'
        ]

        for pattern in prize_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                key_points.append(f"Prize pool includes {matches[0]}")
                break

        # Look for deadlines
        deadline_patterns = [
            r'deadline.*\w+ \d+',
            r'due.*\w+ \d+',
            r'submit.*by.*\w+ \d+'
        ]

        for pattern in deadline_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                key_points.append(f"Important: {matches[0]}")
                break

        # Look for themes/focus areas
        theme_keywords = [
            'sustainability', 'climate', 'AI', 'machine learning', 'blockchain',
            'fintech', 'healthtech', 'edtech', 'social impact', 'innovation'
        ]

        found_themes = [theme for theme in theme_keywords if theme.lower() in content.lower()]
        if found_themes:
            key_points.append(f"Focuses on {', '.join(found_themes[:3])}")

        # Add generic points if we don't have enough
        if len(key_points) < 3:
            key_points.extend([
                "Open to developers of all skill levels",
                "Network with industry professionals",
                "Build innovative solutions"
            ])

        return key_points[:5]

    def _detect_technologies(self, text: str) -> List[str]:
        """Detect mentioned technologies"""
        tech_keywords = {
            'JavaScript': ['javascript', 'js', 'node.js', 'nodejs', 'react', 'angular', 'vue'],
            'Python': ['python', 'django', 'flask', 'fastapi'],
            'Java': ['java', 'spring', 'hibernate'],
            'React': ['react', 'reactjs', 'react.js'],
            'Node.js': ['node.js', 'nodejs', 'node'],
            'MongoDB': ['mongodb', 'mongo'],
            'PostgreSQL': ['postgresql', 'postgres'],
            'Docker': ['docker', 'containerization'],
            'AWS': ['aws', 'amazon web services'],
            'Machine Learning': ['ml', 'machine learning', 'tensorflow', 'pytorch'],
            'Blockchain': ['blockchain', 'ethereum', 'smart contracts', 'web3'],
            'Mobile': ['ios', 'android', 'react native', 'flutter', 'swift', 'kotlin'],
            'Cloud': ['cloud', 'azure', 'gcp', 'google cloud']
        }

        detected_techs = []
        text_lower = text.lower()

        for tech, keywords in tech_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_techs.append(tech)

        return detected_techs

    def _classify_categories(self, text: str) -> List[str]:
        """Classify into hackathon categories"""
        category_keywords = {
            'AI/ML': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'neural', 'deep learning'],
            'Web Development': ['web', 'frontend', 'backend', 'fullstack', 'website', 'webapp'],
            'Mobile': ['mobile', 'ios', 'android', 'app development', 'react native', 'flutter'],
            'Blockchain': ['blockchain', 'crypto', 'ethereum', 'bitcoin', 'web3', 'defi'],
            'FinTech': ['fintech', 'finance', 'banking', 'payment', 'trading', 'investment'],
            'HealthTech': ['health', 'medical', 'healthcare', 'wellness', 'fitness', 'telemedicine'],
            'Climate': ['climate', 'environment', 'sustainability', 'green', 'renewable', 'carbon'],
            'Gaming': ['game', 'gaming', 'unity', 'unreal', 'vr', 'ar', 'virtual reality'],
            'IoT': ['iot', 'internet of things', 'sensors', 'embedded', 'hardware'],
            'Education': ['education', 'learning', 'teaching', 'edtech', 'student', 'academic']
        }

        detected_categories = []
        text_lower = text.lower()

        for category, keywords in category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_categories.append(category)

        return detected_categories

    def _assess_difficulty(self, content: str, stated_difficulty: Optional[str]) -> str:
        """Assess difficulty level"""
        if stated_difficulty:
            return stated_difficulty

        content_lower = content.lower()

        # Beginner indicators
        beginner_keywords = ['beginner', 'newcomer', 'first time', 'intro', 'basic', 'learn']
        if any(keyword in content_lower for keyword in beginner_keywords):
            return 'Beginner'

        # Advanced indicators
        advanced_keywords = ['advanced', 'expert', 'professional', 'experienced', 'complex', 'sophisticated']
        if any(keyword in content_lower for keyword in advanced_keywords):
            return 'Advanced'

        # Default to intermediate
        return 'Intermediate'

    def _prepare_content_for_analysis(self, hackathon: Hackathon) -> str:
        """Prepare hackathon content for analysis"""
        parts = [
            f"Title: {hackathon.title}",
            f"Description: {hackathon.description or hackathon.short_description or 'No description'}",
            f"Organizer: {hackathon.organizer or 'Unknown'}",
            f"Categories: {', '.join(hackathon.categories or [])}",
            f"Technologies: {', '.join(hackathon.technologies or [])}",
            f"Prize Money: ${hackathon.prize_money or 0:,}",
            f"Difficulty: {hackathon.difficulty_level or 'Not specified'}",
            f"Location: {hackathon.location or 'Not specified'}",
            f"Online: {'Yes' if hackathon.is_online else 'No'}"
        ]

        return "\n".join(parts)

    async def _call_openai_chat(self, session: aiohttp.ClientSession, prompt: str) -> Optional[str]:
        """Call OpenAI Chat API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are an AI assistant that analyzes hackathon events and provides structured summaries."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 800,
                "temperature": 0.3
            }

            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    logger.error(f"OpenAI Chat API error: {response.status}")
                    return None

        except Exception as e:
            logger.error(f"Error calling OpenAI Chat API: {e}")
            return None

    def _fallback_summary(self, hackathon: Hackathon) -> ContentSummary:
        """Fallback summary when all else fails"""
        return ContentSummary(
            summary=f"{hackathon.title} - Hackathon event with innovative challenges.",
            key_points=[
                "Open to all developers",
                "Networking opportunities",
                "Build innovative solutions"
            ],
            technologies=hackathon.technologies or [],
            categories=hackathon.categories or [],
            difficulty_assessment=hackathon.difficulty_level or "Intermediate"
        )

# Global content processor instance
content_processor = ContentProcessor()