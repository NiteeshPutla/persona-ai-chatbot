"""
API route handlers.
"""
from fastapi import APIRouter, HTTPException, Depends
from app.api.schemas import ChatRequest, ChatResponse, ChatHistoryResponse
from app.services.agent_service import AgentService
from app.repositories.thread_repository import ThreadRepository
from app.core.dependencies import get_agent_service, get_thread_repository
from app.core.exceptions import (
    ThreadNotFoundError,
    PersonaNotFoundError,
    InvalidUserError,
    LLMError,
    DatabaseError
)
from app.core.logging_config import logger

router = APIRouter()


@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Persona-Switching AI Chatbot API",
        "endpoints": {
            "/chat": "POST - Send a message to the chatbot",
            "/chat_history": "GET - Get chat history for a user",
            "/health": "GET - Health check"
        }
    }


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "database": "connected"}


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    Main chat endpoint.
    
    Accepts a user_id and message, returns the agent's response.
    The agent will automatically detect persona switch requests and manage threads.
    
    Example requests:
    - "act like my mentor" - Creates/switches to mentor thread
    - "how can I scale my product?" - Continues in current thread
    - "back to my mentor thread" - Switches back to mentor thread
    """
    try:
        logger.info(f"Processing chat request for user_id: {request.user_id}")
        
        result = agent_service.chat(
            user_id=request.user_id,
            message=request.message,
            thread_name=request.thread_name
        )
        
        logger.info(f"Chat response generated for user_id: {request.user_id}, thread: {result['thread_name']}")
        
        return ChatResponse(
            response=result["response"],
            thread_name=result["thread_name"],
            thread_id=result["thread_id"]
        )
    except InvalidUserError as e:
        logger.warning(f"Invalid user error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ThreadNotFoundError as e:
        logger.warning(f"Thread not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except LLMError as e:
        logger.error(f"LLM error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing with LLM: {str(e)}")
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@router.get("/chat_history", response_model=ChatHistoryResponse)
async def get_chat_history(
    user_id: str,
    repository: ThreadRepository = Depends(get_thread_repository)
):
    """
    Get chat history for a user.
    
    Returns all threads and their conversation history for the specified user_id.
    """
    try:
        logger.info(f"Retrieving chat history for user_id: {user_id}")
        
        if not user_id or not user_id.strip():
            raise InvalidUserError("user_id cannot be empty")
        
        history = repository.get_user_chat_history(user_id)
        
        logger.info(f"Retrieved {len(history)} threads for user_id: {user_id}")
        
        return ChatHistoryResponse(
            user_id=user_id,
            threads=history
        )
    except InvalidUserError as e:
        logger.warning(f"Invalid user error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in chat_history endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving chat history: {str(e)}")

