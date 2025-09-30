"""
Test configuration and fixtures
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from httpx import AsyncClient
from app.main import app
from app.database import get_db, Base
from app.models.user import User
from app.models.hackathon import Hackathon
import os

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database session."""
    def get_test_db():
        return db_session

    app.dependency_overrides[get_db] = get_test_db

    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        first_name="Test",
        last_name="User",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def test_hackathon(db_session: AsyncSession) -> Hackathon:
    """Create a test hackathon."""
    hackathon = Hackathon(
        title="Test Hackathon",
        description="A test hackathon for testing purposes",
        short_description="Test hackathon",
        organizer="Test Org",
        website_url="https://test.com",
        registration_url="https://test.com/register",
        location="Test City",
        is_online=False,
        is_hybrid=False,
        prize_money=10000.0,
        max_team_size=4,
        difficulty_level="Intermediate",
        categories=["AI/ML", "Web Development"],
        technologies=["Python", "React"],
        source_platform="test",
        source_id="test-123",
        is_active=True
    )
    db_session.add(hackathon)
    await db_session.commit()
    await db_session.refresh(hackathon)
    return hackathon

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API responses."""
    return {
        "choices": [
            {
                "message": {
                    "content": '{"summary": "Test summary", "key_points": ["Point 1", "Point 2"]}'
                }
            }
        ]
    }