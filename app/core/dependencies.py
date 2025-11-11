"""
FastAPI dependency injection setup.
"""
from fastapi import Depends
from sqlalchemy.orm import Session
from app.repositories.thread_repository import ThreadRepository
from app.services.agent_service import AgentService
from app.core.config import settings
from app.core.logging_config import logger


def get_db_session() -> Session:
    """Get database session."""
    from app.models.database import SessionLocal
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_thread_repository(
    session: Session = Depends(get_db_session)
) -> ThreadRepository:
    """Get thread repository instance."""
    return ThreadRepository(session)


def get_agent_service(
    repository: ThreadRepository = Depends(get_thread_repository)
) -> AgentService:
    """Get agent service instance."""
    try:
        return AgentService(repository)
    except Exception as e:
        logger.error(f"Failed to initialize agent service: {e}")
        raise

