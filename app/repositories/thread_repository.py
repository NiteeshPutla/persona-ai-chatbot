"""
Repository pattern for thread and message data access.
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
from app.models.database import UserThread, ChatMessage
from app.core.exceptions import DatabaseError, ThreadNotFoundError
from app.core.logging_config import logger


class ThreadRepository:
    """Repository for managing threads and messages."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_thread(self, user_id: str, thread_name: str, persona_prompt: str) -> UserThread:
        """Create a new conversation thread."""
        try:
            thread = UserThread(
                user_id=user_id,
                thread_name=thread_name,
                persona_prompt=persona_prompt
            )
            self.session.add(thread)
            self.session.commit()
            self.session.refresh(thread)
            logger.info(f"Created thread {thread.id} for user {user_id} with name {thread_name}")
            return thread
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating thread: {e}")
            raise DatabaseError(f"Failed to create thread: {str(e)}")
    
    def get_thread(self, user_id: str, thread_name: str) -> Optional[UserThread]:
        """Get a thread by user_id and thread_name."""
        try:
            return self.session.query(UserThread).filter(
                UserThread.user_id == user_id,
                UserThread.thread_name == thread_name
            ).first()
        except Exception as e:
            logger.error(f"Error getting thread: {e}")
            raise DatabaseError(f"Failed to get thread: {str(e)}")
    
    def get_thread_by_id(self, thread_id: int) -> Optional[UserThread]:
        """Get a thread by ID."""
        try:
            thread = self.session.query(UserThread).filter(
                UserThread.id == thread_id
            ).first()
            if not thread:
                raise ThreadNotFoundError(f"Thread with id {thread_id} not found")
            return thread
        except ThreadNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting thread by id: {e}")
            raise DatabaseError(f"Failed to get thread: {str(e)}")
    
    def get_all_threads(self, user_id: str) -> List[UserThread]:
        """Get all threads for a user."""
        try:
            return self.session.query(UserThread).filter(
                UserThread.user_id == user_id
            ).all()
        except Exception as e:
            logger.error(f"Error getting all threads: {e}")
            raise DatabaseError(f"Failed to get threads: {str(e)}")
    
    def get_most_recent_thread(self, user_id: str) -> Optional[UserThread]:
        """Get the most recently updated thread for a user."""
        try:
            return self.session.query(UserThread).filter(
                UserThread.user_id == user_id
            ).order_by(UserThread.updated_at.desc()).first()
        except Exception as e:
            logger.error(f"Error getting most recent thread: {e}")
            raise DatabaseError(f"Failed to get most recent thread: {str(e)}")
    
    def add_message(self, thread_id: int, role: str, content: str) -> ChatMessage:
        """Add a message to a thread."""
        try:
            message = ChatMessage(
                thread_id=thread_id,
                role=role,
                content=content
            )
            self.session.add(message)
            
            # Update thread's updated_at timestamp
            thread = self.session.query(UserThread).filter(UserThread.id == thread_id).first()
            if thread:
                thread.updated_at = datetime.utcnow()
            
            self.session.commit()
            self.session.refresh(message)
            logger.debug(f"Added {role} message to thread {thread_id}")
            return message
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error adding message: {e}")
            raise DatabaseError(f"Failed to add message: {str(e)}")
    
    def get_thread_messages(self, thread_id: int) -> List[ChatMessage]:
        """Get all messages for a thread, ordered by timestamp."""
        try:
            return self.session.query(ChatMessage).filter(
                ChatMessage.thread_id == thread_id
            ).order_by(ChatMessage.timestamp.asc()).all()
        except Exception as e:
            logger.error(f"Error getting thread messages: {e}")
            raise DatabaseError(f"Failed to get messages: {str(e)}")
    
    def get_user_chat_history(self, user_id: str) -> Dict[str, Dict]:
        """Get all chat history for a user, organized by thread."""
        try:
            threads = self.get_all_threads(user_id)
            history = {}
            
            for thread in threads:
                messages = self.get_thread_messages(thread.id)
                history[thread.thread_name] = {
                    "thread_id": thread.id,
                    "persona_prompt": thread.persona_prompt,
                    "created_at": thread.created_at.isoformat() if thread.created_at else None,
                    "updated_at": thread.updated_at.isoformat() if thread.updated_at else None,
                    "messages": [
                        {
                            "role": msg.role,
                            "content": msg.content,
                            "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
                        }
                        for msg in messages
                    ]
                }
            
            return history
        except Exception as e:
            logger.error(f"Error getting user chat history: {e}")
            raise DatabaseError(f"Failed to get chat history: {str(e)}")

