"""
AI-powered notification service
"""
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import aiohttp
import asyncio
from app.models.hackathon import Hackathon
from app.models.user import User
from app.services.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)

@dataclass
class NotificationData:
    user_id: str
    hackathon_id: str
    notification_type: str
    title: str
    message: str
    priority: str  # low, medium, high
    metadata: Dict[str, Any]

class NotificationService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.use_openai = bool(self.openai_api_key)

    async def generate_personalized_notifications(self, users: List[User], hackathons: List[Hackathon]) -> List[NotificationData]:
        """Generate personalized notifications for users based on their interests"""
        notifications = []

        for user in users:
            try:
                user_notifications = await self._generate_user_notifications(user, hackathons)
                notifications.extend(user_notifications)
            except Exception as e:
                logger.error(f"Error generating notifications for user {user.id}: {e}")

        return notifications

    async def _generate_user_notifications(self, user: User, hackathons: List[Hackathon]) -> List[NotificationData]:
        """Generate notifications for a specific user"""
        notifications = []

        # Get user recommendations
        try:
            recommendations = await ai_service.get_recommendations(user, hackathons, limit=10)

            # Generate notifications for high-scoring recommendations
            for rec in recommendations:
                if rec.score >= 0.7:  # High relevance threshold
                    hackathon = next((h for h in hackathons if str(h.id) == rec.hackathon_id), None)
                    if hackathon:
                        notification = await self._create_recommendation_notification(user, hackathon, rec)
                        if notification:
                            notifications.append(notification)

                        # Check for deadline reminders
                        deadline_notification = self._create_deadline_notification(user, hackathon)
                        if deadline_notification:
                            notifications.append(deadline_notification)

        except Exception as e:
            logger.error(f"Error generating AI recommendations for user {user.id}: {e}")

        # Generate trending notifications
        trending_notification = await self._create_trending_notification(user, hackathons)
        if trending_notification:
            notifications.append(trending_notification)

        return notifications

    async def _create_recommendation_notification(self, user: User, hackathon: Hackathon, recommendation) -> Optional[NotificationData]:
        """Create a personalized recommendation notification"""
        try:
            if self.use_openai:
                message = await self._generate_ai_notification_message(user, hackathon, recommendation)
            else:
                message = self._generate_local_notification_message(user, hackathon, recommendation)

            return NotificationData(
                user_id=str(user.id),
                hackathon_id=str(hackathon.id),
                notification_type="recommendation",
                title=f"Perfect Match: {hackathon.title}",
                message=message,
                priority="high" if recommendation.score >= 0.8 else "medium",
                metadata={
                    "recommendation_score": recommendation.score,
                    "reasons": recommendation.reasons,
                    "hackathon_data": {
                        "title": hackathon.title,
                        "organizer": hackathon.organizer,
                        "categories": hackathon.categories,
                        "prize_money": hackathon.prize_money,
                        "registration_deadline": hackathon.registration_deadline.isoformat() if hackathon.registration_deadline else None
                    }
                }
            )

        except Exception as e:
            logger.error(f"Error creating recommendation notification: {e}")
            return None

    def _create_deadline_notification(self, user: User, hackathon: Hackathon) -> Optional[NotificationData]:
        """Create deadline reminder notification"""
        if not hackathon.registration_deadline:
            return None

        now = datetime.utcnow()
        deadline = hackathon.registration_deadline
        time_diff = deadline - now

        # Notify if deadline is within 3 days
        if timedelta(0) <= time_diff <= timedelta(days=3):
            days_left = time_diff.days
            hours_left = time_diff.seconds // 3600

            if days_left == 0:
                urgency = "today"
                priority = "high"
                message = f"⏰ Last chance! Registration for {hackathon.title} closes in {hours_left} hours."
            elif days_left == 1:
                urgency = "tomorrow"
                priority = "high"
                message = f"⏰ Registration for {hackathon.title} closes tomorrow! Don't miss out."
            else:
                urgency = f"{days_left} days"
                priority = "medium"
                message = f"📅 Registration for {hackathon.title} closes in {days_left} days."

            return NotificationData(
                user_id=str(user.id),
                hackathon_id=str(hackathon.id),
                notification_type="deadline",
                title=f"Registration Deadline: {hackathon.title}",
                message=message,
                priority=priority,
                metadata={
                    "deadline": deadline.isoformat(),
                    "urgency": urgency,
                    "days_left": days_left
                }
            )

        return None

    async def _create_trending_notification(self, user: User, hackathons: List[Hackathon]) -> Optional[NotificationData]:
        """Create notification about trending hackathons"""
        try:
            # Find hackathons with high prizes or interesting themes
            trending = [h for h in hackathons if h.prize_money and h.prize_money >= 50000]

            if trending:
                hackathon = trending[0]  # Take the highest prize one

                message = f"🔥 Trending now: {hackathon.title} is gaining attention with a ${hackathon.prize_money:,} prize pool!"

                return NotificationData(
                    user_id=str(user.id),
                    hackathon_id=str(hackathon.id),
                    notification_type="trending",
                    title="Trending Hackathon Alert",
                    message=message,
                    priority="low",
                    metadata={
                        "prize_money": hackathon.prize_money,
                        "categories": hackathon.categories
                    }
                )

        except Exception as e:
            logger.error(f"Error creating trending notification: {e}")

        return None

    async def _generate_ai_notification_message(self, user: User, hackathon: Hackathon, recommendation) -> str:
        """Generate AI-powered notification message"""
        try:
            async with aiohttp.ClientSession() as session:
                user_interests = self._extract_user_interests(user)

                prompt = f"""
                Create a personalized, engaging notification message for a user about a hackathon recommendation.

                User Profile: {user_interests}
                Hackathon: {hackathon.title}
                Organizer: {hackathon.organizer or 'Unknown'}
                Categories: {', '.join(hackathon.categories or [])}
                Prize: ${hackathon.prize_money or 0:,}
                Recommendation Score: {recommendation.score:.1%}
                Reasons: {', '.join(recommendation.reasons[:2])}

                Write a compelling, personal notification message (max 120 characters) that:
                1. Mentions why it's perfect for them
                2. Creates excitement
                3. Includes relevant details

                Examples:
                "🚀 Perfect match! AI Startup Challenge matches your ML skills - $50K prize!"
                "🎯 Made for you: FinTech Hackathon uses React & blockchain - your expertise!"

                Return only the message text.
                """

                response = await self._call_openai_chat(session, prompt)

                if response and len(response.strip()) <= 150:
                    return response.strip()

        except Exception as e:
            logger.error(f"Error generating AI notification message: {e}")

        # Fallback to local generation
        return self._generate_local_notification_message(user, hackathon, recommendation)

    def _generate_local_notification_message(self, user: User, hackathon: Hackathon, recommendation) -> str:
        """Generate notification message using local logic"""
        try:
            # Extract key points
            prize_text = f"${hackathon.prize_money:,} prize" if hackathon.prize_money and hackathon.prize_money > 0 else ""

            # Get the primary reason
            main_reason = recommendation.reasons[0] if recommendation.reasons else "great opportunity"

            # Build message
            if prize_text:
                message = f"🎯 {hackathon.title} - {main_reason.lower()} with {prize_text}!"
            else:
                message = f"🎯 {hackathon.title} - {main_reason.lower()}!"

            # Truncate if too long
            if len(message) > 120:
                message = f"🎯 {hackathon.title} - perfect match for you!"

            return message

        except Exception as e:
            logger.error(f"Error generating local notification message: {e}")
            return f"🎯 Check out {hackathon.title} - it might interest you!"

    def _extract_user_interests(self, user: User) -> str:
        """Extract user interests for prompt"""
        interests = []

        if hasattr(user, 'skills') and user.skills:
            interests.append(f"Skills: {', '.join(user.skills[:3])}")

        if hasattr(user, 'interests') and user.interests:
            interests.append(f"Interests: {', '.join(user.interests[:3])}")

        if hasattr(user, 'experience_level') and user.experience_level:
            interests.append(f"Experience: {user.experience_level}")

        return "; ".join(interests) if interests else "General developer"

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
                    {"role": "system", "content": "You are an AI assistant that creates engaging, personalized notification messages for hackathon recommendations."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 100,
                "temperature": 0.7
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

# Global notification service instance
notification_service = NotificationService()