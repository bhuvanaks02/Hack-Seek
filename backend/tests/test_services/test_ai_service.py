"""
Tests for AI service
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from app.services.ai_service import ai_service, SearchResult, RecommendationResult
from app.models.hackathon import Hackathon
from app.models.user import User

@pytest.mark.unit
@pytest.mark.ai
class TestAIService:
    """Test AI service functionality."""

    @pytest.fixture
    def sample_hackathons(self):
        """Create sample hackathons for testing."""
        return [
            Hackathon(
                id="1",
                title="AI Hackathon 2024",
                description="Build AI solutions for real-world problems",
                categories=["AI/ML", "Data Science"],
                technologies=["Python", "TensorFlow"],
                difficulty_level="Intermediate",
                prize_money=50000
            ),
            Hackathon(
                id="2",
                title="Web Dev Challenge",
                description="Create innovative web applications",
                categories=["Web Development"],
                technologies=["React", "Node.js"],
                difficulty_level="Beginner",
                prize_money=25000
            )
        ]

    @pytest.fixture
    def sample_user(self):
        """Create sample user for testing."""
        user = Mock(spec=User)
        user.id = "user123"
        user.skills = ["Python", "Machine Learning"]
        user.interests = ["AI", "Technology"]
        user.experience_level = "intermediate"
        user.preferred_categories = ["AI/ML"]
        return user

    async def test_initialize_with_hackathons(self, sample_hackathons):
        """Test AI service initialization with hackathons."""
        await ai_service.initialize(sample_hackathons)
        assert ai_service.hackathon_vectors is not None
        assert len(ai_service.hackathon_texts) == 2

    async def test_local_semantic_search(self, sample_hackathons):
        """Test local semantic search functionality."""
        await ai_service.initialize(sample_hackathons)

        results = await ai_service.semantic_search(
            "artificial intelligence machine learning",
            sample_hackathons,
            limit=2
        )

        assert isinstance(results, list)
        assert len(results) <= 2
        if results:
            assert isinstance(results[0], SearchResult)
            assert hasattr(results[0], 'hackathon_id')
            assert hasattr(results[0], 'relevance_score')

    @patch('aiohttp.ClientSession.post')
    async def test_openai_semantic_search(self, mock_post, sample_hackathons):
        """Test OpenAI-powered semantic search."""
        # Mock OpenAI API response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "data": [{"embedding": [0.1] * 1536}]
        }
        mock_post.return_value.__aenter__.return_value = mock_response

        # Temporarily enable OpenAI
        original_use_openai = ai_service.use_openai
        ai_service.use_openai = True
        ai_service.openai_api_key = "test-key"

        try:
            results = await ai_service.semantic_search(
                "AI hackathon",
                sample_hackathons,
                limit=1
            )

            # Should fallback to local search if OpenAI fails
            assert isinstance(results, list)
        finally:
            ai_service.use_openai = original_use_openai

    async def test_local_recommendations(self, sample_user, sample_hackathons):
        """Test local recommendation algorithm."""
        results = await ai_service.get_recommendations(
            sample_user,
            sample_hackathons,
            limit=2
        )

        assert isinstance(results, list)
        assert len(results) <= 2
        if results:
            assert isinstance(results[0], RecommendationResult)
            assert hasattr(results[0], 'hackathon_id')
            assert hasattr(results[0], 'score')
            assert hasattr(results[0], 'reasons')

    def test_local_query_processing(self):
        """Test local natural language query processing."""
        test_queries = [
            "AI hackathons with good prizes",
            "beginner web development contests",
            "online blockchain events",
            "hackathons with $10000 prize"
        ]

        for query in test_queries:
            result = ai_service._local_query_processing(query)

            assert isinstance(result, dict)
            assert "processed_query" in result
            assert "filters" in result
            assert isinstance(result["filters"], dict)

    def test_find_matched_terms(self, sample_hackathons):
        """Test term matching in hackathon content."""
        query_terms = ["ai", "machine", "learning"]
        hackathon = sample_hackathons[0]

        matched = ai_service._find_matched_terms(query_terms, hackathon)

        assert isinstance(matched, list)
        assert all(isinstance(term, str) for term in matched)

    def test_prepare_hackathon_text(self, sample_hackathons):
        """Test hackathon text preparation."""
        hackathon = sample_hackathons[0]
        text = ai_service._prepare_hackathon_text(hackathon)

        assert isinstance(text, str)
        assert len(text) > 0
        assert hackathon.title.lower() in text
        assert hackathon.description.lower() in text

    def test_calculate_recommendation_score(self, sample_user, sample_hackathons):
        """Test recommendation score calculation."""
        user_interests = ai_service._extract_user_interests(sample_user)
        hackathon = sample_hackathons[0]  # AI hackathon

        score = ai_service._calculate_recommendation_score(user_interests, hackathon)

        assert isinstance(score, float)
        assert 0 <= score <= 1

    def test_generate_recommendation_reasons(self, sample_user, sample_hackathons):
        """Test recommendation reason generation."""
        user_interests = ai_service._extract_user_interests(sample_user)
        hackathon = sample_hackathons[0]  # AI hackathon

        reasons = ai_service._generate_recommendation_reasons(user_interests, hackathon)

        assert isinstance(reasons, list)
        assert len(reasons) <= 3
        assert all(isinstance(reason, str) for reason in reasons)

    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        vec3 = [1.0, 0.0, 0.0]

        # Orthogonal vectors
        similarity1 = ai_service._cosine_similarity(vec1, vec2)
        assert abs(similarity1 - 0.0) < 1e-6

        # Identical vectors
        similarity2 = ai_service._cosine_similarity(vec1, vec3)
        assert abs(similarity2 - 1.0) < 1e-6

    @pytest.mark.parametrize("query,expected_filters", [
        ("online AI hackathons", {"is_online": True}),
        ("beginner web development", {"difficulty_level": "Beginner"}),
        ("hackathons with $50000 prize", {"min_prize": 50000}),
        ("advanced blockchain contests", {"difficulty_level": "Advanced"})
    ])
    def test_query_processing_filters(self, query, expected_filters):
        """Test that query processing extracts correct filters."""
        result = ai_service._local_query_processing(query)

        for key, value in expected_filters.items():
            if key in result["filters"]:
                assert result["filters"][key] == value