"""
Pytest configuration and fixtures.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Base, UserThread, ChatMessage
from app.repositories.thread_repository import ThreadRepository
from app.services.agent_service import AgentService


@pytest.fixture
def test_db():
    """Create a test database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def repository(test_db):
    """Create a repository instance for testing."""
    return ThreadRepository(test_db)


@pytest.fixture
def agent_service(repository):
    """Create an agent service instance for testing."""
    # Note: This will require OPENAI_API_KEY to be set for full testing
    # For unit tests, we can mock the LLM
    return AgentService(repository)


@pytest.fixture
def sample_thread(test_db):
    """Create a sample thread for testing."""
    thread = UserThread(
        user_id="test_user",
        thread_name="mentor",
        persona_prompt="You are a mentor."
    )
    test_db.add(thread)
    test_db.commit()
    test_db.refresh(thread)
    return thread

