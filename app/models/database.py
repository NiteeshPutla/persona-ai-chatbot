"""
Database models and session management.
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from datetime import datetime
from typing import Generator
from app.core.config import settings
from app.core.logging_config import logger

Base = declarative_base()


class UserThread(Base):
    """Represents a conversation thread for a user with a specific persona."""
    __tablename__ = "user_threads"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    thread_name = Column(String, nullable=False)  # e.g., "mentor", "investor"
    persona_prompt = Column(Text, nullable=False)  # The system prompt for this persona
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to messages
    messages = relationship("ChatMessage", back_populates="thread", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<UserThread(user_id={self.user_id}, thread_name={self.thread_name})>"


class ChatMessage(Base):
    """Represents a single message in a conversation thread."""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(Integer, ForeignKey("user_threads.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to thread
    thread = relationship("UserThread", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessage(thread_id={self.thread_id}, role={self.role})>"


# Database engine and session factory
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.database_echo
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")


def get_session() -> Session:
    """Get a database session."""
    return SessionLocal()

