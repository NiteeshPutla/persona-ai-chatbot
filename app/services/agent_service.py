"""
Service layer for agent orchestration.
"""
from app.agent.graph import PersonaSwitchingAgent
from app.repositories.thread_repository import ThreadRepository
from app.core.exceptions import InvalidUserError
from app.core.logging_config import logger


class AgentService:
    """Service for managing agent interactions."""
    
    def __init__(self, repository: ThreadRepository):
        self.repository = repository
        self._agent = None
    
    @property
    def agent(self) -> PersonaSwitchingAgent:
        """Lazy initialization of agent."""
        if self._agent is None:
            self._agent = PersonaSwitchingAgent(self.repository)
        return self._agent
    
    def chat(self, user_id: str, message: str, thread_name: str = None) -> dict:
        """
        Process a chat message.
        
        Args:
            user_id: User identifier
            message: User's message
            thread_name: Optional thread name to use
        
        Returns:
            Dictionary with response and thread information
        
        Raises:
            InvalidUserError: If user_id is invalid
        """
        if not user_id or not user_id.strip():
            raise InvalidUserError("user_id cannot be empty")
        
        if not message or not message.strip():
            raise InvalidUserError("message cannot be empty")
        
        logger.info(f"Processing chat for user_id: {user_id}, thread_name: {thread_name}")
        
        try:
            result = self.agent.chat(
                user_id=user_id,
                message=message,
                thread_name=thread_name
            )
            logger.info(f"Chat completed for user_id: {user_id}, thread: {result['thread_name']}")
            return result
        except Exception as e:
            logger.error(f"Error in agent service chat: {e}", exc_info=True)
            raise

