"""
AI service for natural language processing and recommendations
"""
import os
import json
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import aiohttp
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.models.hackathon import Hackathon
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    hackathon_id: str
    relevance_score: float
    matched_terms: List[str]

@dataclass
class RecommendationResult:
    hackathon_id: str
    score: float
    reasons: List[str]

class AIService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.use_openai = bool(self.openai_api_key)

        # Fallback to local processing if no API key
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        self.hackathon_vectors = None
        self.hackathon_texts = {}

    async def initialize(self, hackathons: List[Hackathon]):
        """Initialize AI models with hackathon data"""
        try:
            # Prepare text data for vectorization
            texts = []
            for hackathon in hackathons:
                text = self._prepare_hackathon_text(hackathon)
                texts.append(text)
                self.hackathon_texts[hackathon.id] = text

            if texts:
                # Fit vectorizer and create document vectors
                self.hackathon_vectors = self.vectorizer.fit_transform(texts)
                logger.info(f"AI service initialized with {len(texts)} hackathons")

        except Exception as e:
            logger.error(f"Error initializing AI service: {e}")

    def _prepare_hackathon_text(self, hackathon: Hackathon) -> str:
        """Prepare hackathon data for text analysis"""
        parts = [
            hackathon.title or "",
            hackathon.description or hackathon.short_description or "",
            hackathon.organizer or "",
            hackathon.location or "",
            " ".join(hackathon.categories or []),
            " ".join(hackathon.technologies or []),
            hackathon.difficulty_level or ""
        ]
        return " ".join(filter(None, parts)).lower()

    async def semantic_search(self, query: str, hackathons: List[Hackathon], limit: int = 10) -> List[SearchResult]:
        """Perform semantic search on hackathons"""
        try:
            if self.use_openai:
                return await self._openai_semantic_search(query, hackathons, limit)
            else:
                return await self._local_semantic_search(query, hackathons, limit)
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []

    async def _local_semantic_search(self, query: str, hackathons: List[Hackathon], limit: int) -> List[SearchResult]:
        """Local implementation using TF-IDF and cosine similarity"""
        if self.hackathon_vectors is None:
            await self.initialize(hackathons)

        if self.hackathon_vectors is None:
            return []

        try:
            # Vectorize query
            query_vector = self.vectorizer.transform([query.lower()])

            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.hackathon_vectors).flatten()

            # Get top results
            top_indices = np.argsort(similarities)[::-1][:limit]

            results = []
            query_terms = query.lower().split()

            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum relevance threshold
                    hackathon = hackathons[idx]
                    matched_terms = self._find_matched_terms(query_terms, hackathon)

                    results.append(SearchResult(
                        hackathon_id=hackathon.id,
                        relevance_score=float(similarities[idx]),
                        matched_terms=matched_terms
                    ))

            return results

        except Exception as e:
            logger.error(f"Error in local semantic search: {e}")
            return []

    async def _openai_semantic_search(self, query: str, hackathons: List[Hackathon], limit: int) -> List[SearchResult]:
        """OpenAI-powered semantic search"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get embeddings for query
                query_embedding = await self._get_openai_embedding(session, query)

                if not query_embedding:
                    return await self._local_semantic_search(query, hackathons, limit)

                # Calculate similarities with hackathon embeddings
                similarities = []
                for hackathon in hackathons:
                    hackathon_text = self._prepare_hackathon_text(hackathon)
                    hackathon_embedding = await self._get_openai_embedding(session, hackathon_text)

                    if hackathon_embedding:
                        similarity = self._cosine_similarity(query_embedding, hackathon_embedding)
                        similarities.append((hackathon, similarity))

                # Sort by similarity and return top results
                similarities.sort(key=lambda x: x[1], reverse=True)

                results = []
                query_terms = query.lower().split()

                for hackathon, similarity in similarities[:limit]:
                    if similarity > 0.3:  # Higher threshold for OpenAI
                        matched_terms = self._find_matched_terms(query_terms, hackathon)

                        results.append(SearchResult(
                            hackathon_id=hackathon.id,
                            relevance_score=float(similarity),
                            matched_terms=matched_terms
                        ))

                return results

        except Exception as e:
            logger.error(f"Error in OpenAI semantic search: {e}")
            return await self._local_semantic_search(query, hackathons, limit)

    async def _get_openai_embedding(self, session: aiohttp.ClientSession, text: str) -> Optional[List[float]]:
        """Get text embedding from OpenAI API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "input": text[:8000],  # Limit input length
                "model": "text-embedding-ada-002"
            }

            async with session.post(
                "https://api.openai.com/v1/embeddings",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result["data"][0]["embedding"]
                else:
                    logger.error(f"OpenAI API error: {response.status}")
                    return None

        except Exception as e:
            logger.error(f"Error getting OpenAI embedding: {e}")
            return None

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            a = np.array(vec1)
            b = np.array(vec2)
            return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
        except:
            return 0.0

    def _find_matched_terms(self, query_terms: List[str], hackathon: Hackathon) -> List[str]:
        """Find terms from query that match hackathon content"""
        hackathon_text = self._prepare_hackathon_text(hackathon)
        matched = []

        for term in query_terms:
            if len(term) > 2 and term in hackathon_text:
                matched.append(term)

        return matched

    async def get_recommendations(self, user: User, hackathons: List[Hackathon], limit: int = 5) -> List[RecommendationResult]:
        """Get personalized hackathon recommendations for user"""
        try:
            if self.use_openai:
                return await self._openai_recommendations(user, hackathons, limit)
            else:
                return await self._local_recommendations(user, hackathons, limit)
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []

    async def _local_recommendations(self, user: User, hackathons: List[Hackathon], limit: int) -> List[RecommendationResult]:
        """Local recommendation algorithm"""
        recommendations = []

        # Simple recommendation based on user preferences
        user_interests = self._extract_user_interests(user)

        for hackathon in hackathons:
            score = self._calculate_recommendation_score(user_interests, hackathon)
            reasons = self._generate_recommendation_reasons(user_interests, hackathon)

            if score > 0.3:
                recommendations.append(RecommendationResult(
                    hackathon_id=hackathon.id,
                    score=score,
                    reasons=reasons
                ))

        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:limit]

    async def _openai_recommendations(self, user: User, hackathons: List[Hackathon], limit: int) -> List[RecommendationResult]:
        """OpenAI-powered recommendations"""
        try:
            async with aiohttp.ClientSession() as session:
                user_profile = self._create_user_profile(user)

                # Get recommendations using OpenAI
                prompt = f"""
                User profile: {user_profile}

                Recommend the most suitable hackathons from the following list.
                Consider user's interests, experience level, and preferences.

                Hackathons:
                {self._format_hackathons_for_prompt(hackathons[:20])}

                Return top {limit} recommendations with scores (0-1) and reasons.
                Format: JSON array with objects containing hackathon_id, score, and reasons array.
                """

                response = await self._call_openai_chat(session, prompt)

                if response:
                    try:
                        # Parse OpenAI response
                        recommendations_data = json.loads(response)
                        recommendations = []

                        for item in recommendations_data:
                            recommendations.append(RecommendationResult(
                                hackathon_id=item.get("hackathon_id", ""),
                                score=float(item.get("score", 0)),
                                reasons=item.get("reasons", [])
                            ))

                        return recommendations
                    except json.JSONDecodeError:
                        logger.error("Failed to parse OpenAI recommendations response")

                # Fallback to local recommendations
                return await self._local_recommendations(user, hackathons, limit)

        except Exception as e:
            logger.error(f"Error in OpenAI recommendations: {e}")
            return await self._local_recommendations(user, hackathons, limit)

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
                    {"role": "system", "content": "You are an AI assistant that helps recommend hackathons to users based on their profiles and preferences."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000,
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

    def _extract_user_interests(self, user: User) -> Dict[str, Any]:
        """Extract user interests from profile and activity"""
        # This would be enhanced with actual user data
        return {
            "skills": getattr(user, 'skills', []),
            "interests": getattr(user, 'interests', []),
            "experience_level": getattr(user, 'experience_level', 'intermediate'),
            "preferred_categories": getattr(user, 'preferred_categories', []),
            "location_preference": getattr(user, 'location_preference', None)
        }

    def _calculate_recommendation_score(self, user_interests: Dict[str, Any], hackathon: Hackathon) -> float:
        """Calculate recommendation score for a hackathon"""
        score = 0.0

        # Category matching
        user_categories = user_interests.get('preferred_categories', [])
        hackathon_categories = hackathon.categories or []
        if user_categories and hackathon_categories:
            category_overlap = len(set(user_categories) & set(hackathon_categories))
            score += category_overlap / len(user_categories) * 0.4

        # Skill matching
        user_skills = user_interests.get('skills', [])
        hackathon_techs = hackathon.technologies or []
        if user_skills and hackathon_techs:
            skill_overlap = len(set(user_skills) & set(hackathon_techs))
            score += skill_overlap / len(user_skills) * 0.3

        # Experience level matching
        user_level = user_interests.get('experience_level', 'intermediate')
        hackathon_level = hackathon.difficulty_level
        if hackathon_level:
            level_match = {
                ('beginner', 'Beginner'): 1.0,
                ('intermediate', 'Intermediate'): 1.0,
                ('advanced', 'Advanced'): 1.0,
                ('beginner', 'Intermediate'): 0.7,
                ('intermediate', 'Advanced'): 0.8,
                ('advanced', 'Intermediate'): 0.6
            }
            score += level_match.get((user_level, hackathon_level), 0.5) * 0.2

        # Prize money factor (normalized)
        if hackathon.prize_money and hackathon.prize_money > 0:
            score += min(hackathon.prize_money / 50000, 1.0) * 0.1

        return min(score, 1.0)

    def _generate_recommendation_reasons(self, user_interests: Dict[str, Any], hackathon: Hackathon) -> List[str]:
        """Generate reasons for recommendation"""
        reasons = []

        # Check category matches
        user_categories = set(user_interests.get('preferred_categories', []))
        hackathon_categories = set(hackathon.categories or [])
        common_categories = user_categories & hackathon_categories
        if common_categories:
            reasons.append(f"Matches your interest in {', '.join(list(common_categories)[:2])}")

        # Check skill matches
        user_skills = set(user_interests.get('skills', []))
        hackathon_techs = set(hackathon.technologies or [])
        common_skills = user_skills & hackathon_techs
        if common_skills:
            reasons.append(f"Uses technologies you know: {', '.join(list(common_skills)[:2])}")

        # Check difficulty level
        user_level = user_interests.get('experience_level', 'intermediate')
        if hackathon.difficulty_level == user_level.title():
            reasons.append(f"Perfect for your {user_level} skill level")

        # Check prize money
        if hackathon.prize_money and hackathon.prize_money >= 10000:
            reasons.append(f"Great prize pool of ${hackathon.prize_money:,}")

        # Check location
        if hackathon.is_online:
            reasons.append("Online event - join from anywhere")

        return reasons[:3]  # Limit to top 3 reasons

    def _create_user_profile(self, user: User) -> str:
        """Create user profile text for AI processing"""
        interests = self._extract_user_interests(user)

        profile_parts = [
            f"Experience level: {interests.get('experience_level', 'intermediate')}",
            f"Skills: {', '.join(interests.get('skills', [])[:5])}",
            f"Interests: {', '.join(interests.get('interests', [])[:5])}",
            f"Preferred categories: {', '.join(interests.get('preferred_categories', [])[:3])}"
        ]

        return "; ".join(filter(None, profile_parts))

    def _format_hackathons_for_prompt(self, hackathons: List[Hackathon]) -> str:
        """Format hackathons for AI prompt"""
        formatted = []

        for hackathon in hackathons:
            hackathon_info = [
                f"ID: {hackathon.id}",
                f"Title: {hackathon.title}",
                f"Categories: {', '.join(hackathon.categories or [])}",
                f"Technologies: {', '.join(hackathon.technologies or [])}",
                f"Difficulty: {hackathon.difficulty_level or 'Not specified'}",
                f"Prize: ${hackathon.prize_money or 0:,}"
            ]
            formatted.append(" | ".join(hackathon_info))

        return "\n".join(formatted)

    async def process_natural_language_query(self, query: str) -> Dict[str, Any]:
        """Process natural language query and extract search parameters"""
        try:
            if self.use_openai:
                return await self._openai_query_processing(query)
            else:
                return self._local_query_processing(query)
        except Exception as e:
            logger.error(f"Error processing natural language query: {e}")
            return {"query": query, "filters": {}}

    async def _openai_query_processing(self, query: str) -> Dict[str, Any]:
        """Use OpenAI to process natural language query"""
        try:
            async with aiohttp.ClientSession() as session:
                prompt = f"""
                Parse this hackathon search query and extract structured search parameters:
                Query: "{query}"

                Extract the following if mentioned:
                - location (city, country, or "online")
                - categories (AI/ML, Web Development, Mobile, Blockchain, etc.)
                - technologies (JavaScript, Python, React, etc.)
                - difficulty_level (Beginner, Intermediate, Advanced)
                - prize_range (minimum prize amount)
                - date_preferences (this week, this month, etc.)
                - is_online (true/false)

                Return JSON format:
                {{
                    "processed_query": "cleaned search terms",
                    "filters": {{
                        "location": "...",
                        "categories": [...],
                        "technologies": [...],
                        "difficulty_level": "...",
                        "min_prize": number,
                        "is_online": boolean
                    }}
                }}
                """

                response = await self._call_openai_chat(session, prompt)

                if response:
                    try:
                        return json.loads(response)
                    except json.JSONDecodeError:
                        logger.error("Failed to parse OpenAI query processing response")

                # Fallback to local processing
                return self._local_query_processing(query)

        except Exception as e:
            logger.error(f"Error in OpenAI query processing: {e}")
            return self._local_query_processing(query)

    def _local_query_processing(self, query: str) -> Dict[str, Any]:
        """Local natural language query processing"""
        filters = {}
        processed_query = query.lower()

        # Extract location
        if "online" in processed_query:
            filters["is_online"] = True

        # Extract categories
        category_keywords = {
            "ai": "AI/ML", "ml": "AI/ML", "machine learning": "AI/ML",
            "web": "Web Development", "frontend": "Web Development", "backend": "Web Development",
            "mobile": "Mobile", "app": "Mobile", "ios": "Mobile", "android": "Mobile",
            "blockchain": "Blockchain", "crypto": "Blockchain",
            "game": "Gaming", "gaming": "Gaming",
            "fintech": "FinTech", "finance": "FinTech"
        }

        categories = []
        for keyword, category in category_keywords.items():
            if keyword in processed_query:
                categories.append(category)

        if categories:
            filters["categories"] = categories

        # Extract difficulty
        if "beginner" in processed_query or "easy" in processed_query:
            filters["difficulty_level"] = "Beginner"
        elif "advanced" in processed_query or "expert" in processed_query:
            filters["difficulty_level"] = "Advanced"
        elif "intermediate" in processed_query:
            filters["difficulty_level"] = "Intermediate"

        # Extract prize information
        import re
        prize_match = re.search(r'\$(\d+(?:,\d+)*)', processed_query)
        if prize_match:
            try:
                prize_amount = int(prize_match.group(1).replace(',', ''))
                filters["min_prize"] = prize_amount
            except ValueError:
                pass

        # Clean query by removing filter terms
        filter_terms = ["online", "beginner", "intermediate", "advanced", "easy", "expert"]
        for term in filter_terms:
            processed_query = processed_query.replace(term, "")

        processed_query = " ".join(processed_query.split())  # Clean whitespace

        return {
            "processed_query": processed_query,
            "filters": filters
        }

# Global AI service instance
ai_service = AIService()