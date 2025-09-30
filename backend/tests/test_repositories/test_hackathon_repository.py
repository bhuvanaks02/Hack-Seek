"""
Tests for hackathon repository
"""
import pytest
from app.repositories.hackathon_repository import HackathonRepository
from app.models.hackathon import Hackathon

@pytest.mark.unit
class TestHackathonRepository:
    """Test hackathon repository functionality."""

    async def test_create_hackathon(self, db_session):
        """Test creating a new hackathon."""
        repo = HackathonRepository(db_session)

        hackathon_data = {
            "title": "Test Hackathon",
            "description": "A test hackathon",
            "organizer": "Test Org",
            "website_url": "https://test.com",
            "location": "Test City",
            "is_online": False,
            "prize_money": 5000.0,
            "difficulty_level": "Beginner",
            "categories": ["Web Development"],
            "technologies": ["JavaScript"],
            "source_platform": "test",
            "source_id": "test-123"
        }

        hackathon = await repo.create(hackathon_data)

        assert hackathon.id is not None
        assert hackathon.title == "Test Hackathon"
        assert hackathon.is_active is True

    async def test_get_by_id(self, db_session, test_hackathon):
        """Test getting hackathon by ID."""
        repo = HackathonRepository(db_session)

        retrieved = await repo.get_by_id(test_hackathon.id)

        assert retrieved is not None
        assert retrieved.id == test_hackathon.id
        assert retrieved.title == test_hackathon.title

    async def test_get_active_hackathons(self, db_session, test_hackathon):
        """Test getting active hackathons."""
        repo = HackathonRepository(db_session)

        # Create inactive hackathon
        inactive_hackathon = Hackathon(
            title="Inactive Hackathon",
            description="An inactive hackathon",
            source_platform="test",
            source_id="inactive-123",
            is_active=False
        )
        db_session.add(inactive_hackathon)
        await db_session.commit()

        active_hackathons = await repo.get_active_hackathons(skip=0, limit=10)

        assert len(active_hackathons) >= 1
        assert all(h.is_active for h in active_hackathons)
        assert any(h.id == test_hackathon.id for h in active_hackathons)

    async def test_search_hackathons(self, db_session, test_hackathon):
        """Test searching hackathons."""
        repo = HackathonRepository(db_session)

        # Search by title
        results = await repo.search_hackathons(
            query_text="Test",
            skip=0,
            limit=10
        )

        assert len(results) >= 1
        assert any(h.id == test_hackathon.id for h in results)

    async def test_search_with_filters(self, db_session, test_hackathon):
        """Test searching with filters."""
        repo = HackathonRepository(db_session)

        # Search by category
        results = await repo.search_hackathons(
            categories=["AI/ML"],
            skip=0,
            limit=10
        )

        assert len(results) >= 1
        assert all("AI/ML" in (h.categories or []) for h in results)

    async def test_get_featured_hackathons(self, db_session, test_hackathon):
        """Test getting featured hackathons."""
        repo = HackathonRepository(db_session)

        # Create high-prize hackathon
        high_prize_hackathon = Hackathon(
            title="High Prize Hackathon",
            description="A hackathon with high prize",
            prize_money=100000.0,
            source_platform="test",
            source_id="high-prize-123",
            is_active=True
        )
        db_session.add(high_prize_hackathon)
        await db_session.commit()

        featured = await repo.get_featured_hackathons(limit=5)

        assert len(featured) >= 1
        # Should be ordered by prize money
        if len(featured) > 1:
            assert featured[0].prize_money >= featured[1].prize_money

    async def test_update_hackathon(self, db_session, test_hackathon):
        """Test updating a hackathon."""
        repo = HackathonRepository(db_session)

        update_data = {
            "title": "Updated Test Hackathon",
            "prize_money": 15000.0
        }

        updated = await repo.update(test_hackathon.id, update_data)

        assert updated.title == "Updated Test Hackathon"
        assert updated.prize_money == 15000.0

    async def test_delete_hackathon(self, db_session, test_hackathon):
        """Test deleting a hackathon."""
        repo = HackathonRepository(db_session)

        success = await repo.delete(test_hackathon.id)

        assert success is True

        # Verify deletion
        deleted = await repo.get_by_id(test_hackathon.id)
        assert deleted is None

    async def test_count_hackathons(self, db_session, test_hackathon):
        """Test counting hackathons."""
        repo = HackathonRepository(db_session)

        count = await repo.count()

        assert count >= 1
        assert isinstance(count, int)