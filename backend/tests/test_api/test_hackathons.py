"""
Integration tests for hackathon API endpoints
"""
import pytest
from httpx import AsyncClient

@pytest.mark.integration
class TestHackathonAPI:
    """Test hackathon API endpoints."""

    async def test_get_hackathons(self, client: AsyncClient, test_hackathon):
        """Test GET /hackathons endpoint."""
        response = await client.get("/api/hackathons/")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert len(data["data"]) >= 1

    async def test_get_hackathon_by_id(self, client: AsyncClient, test_hackathon):
        """Test GET /hackathons/{id} endpoint."""
        response = await client.get(f"/api/hackathons/{test_hackathon.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_hackathon.id)
        assert data["title"] == test_hackathon.title

    async def test_get_hackathon_not_found(self, client: AsyncClient):
        """Test GET /hackathons/{id} with non-existent ID."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/hackathons/{fake_id}")

        assert response.status_code == 404

    async def test_search_hackathons(self, client: AsyncClient, test_hackathon):
        """Test GET /hackathons/search endpoint."""
        response = await client.get("/api/hackathons/search?q=Test")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert len(data["data"]) >= 1

    async def test_search_with_filters(self, client: AsyncClient, test_hackathon):
        """Test search with various filters."""
        # Test category filter
        response = await client.get("/api/hackathons/search?categories=AI/ML")
        assert response.status_code == 200

        # Test difficulty filter
        response = await client.get("/api/hackathons/search?difficulty_level=Intermediate")
        assert response.status_code == 200

        # Test online filter
        response = await client.get("/api/hackathons/search?is_online=true")
        assert response.status_code == 200

    async def test_ai_search(self, client: AsyncClient, test_hackathon):
        """Test AI-powered search endpoint."""
        response = await client.get("/api/hackathons/ai/search?query=artificial intelligence")

        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "processed_query" in data
        assert "results" in data

    async def test_ai_recommendations(self, client: AsyncClient, test_user, test_hackathon):
        """Test AI recommendations endpoint."""
        response = await client.get(f"/api/hackathons/ai/recommendations?user_id={test_user.id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_similar_hackathons(self, client: AsyncClient, test_hackathon):
        """Test similar hackathons endpoint."""
        response = await client.get(f"/api/hackathons/ai/similar/{test_hackathon.id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_featured_hackathons(self, client: AsyncClient, test_hackathon):
        """Test GET /hackathons/featured endpoint."""
        response = await client.get("/api/hackathons/featured")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    async def test_get_upcoming_hackathons(self, client: AsyncClient, test_hackathon):
        """Test GET /hackathons/upcoming endpoint."""
        response = await client.get("/api/hackathons/upcoming")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    async def test_create_hackathon(self, client: AsyncClient):
        """Test POST /hackathons endpoint."""
        hackathon_data = {
            "title": "New Test Hackathon",
            "description": "A new test hackathon",
            "organizer": "Test Org",
            "website_url": "https://test.com",
            "location": "Test City",
            "is_online": False,
            "prize_money": 5000.0,
            "difficulty_level": "Beginner",
            "categories": ["Web Development"],
            "technologies": ["JavaScript"],
            "source_platform": "api",
            "source_id": "api-test-123"
        }

        response = await client.post("/api/hackathons/", json=hackathon_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == hackathon_data["title"]
        assert "id" in data

    async def test_pagination(self, client: AsyncClient, test_hackathon):
        """Test pagination parameters."""
        # Test page size
        response = await client.get("/api/hackathons/?page=1&size=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) <= 5

        # Test page number
        response = await client.get("/api/hackathons/?page=2&size=1")
        assert response.status_code == 200

    async def test_invalid_filters(self, client: AsyncClient):
        """Test API with invalid filter values."""
        # Invalid difficulty level
        response = await client.get("/api/hackathons/search?difficulty_level=Invalid")
        assert response.status_code == 200  # Should handle gracefully

        # Invalid prize value
        response = await client.get("/api/hackathons/search?min_prize=-100")
        assert response.status_code == 422  # Validation error